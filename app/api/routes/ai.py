from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.database import get_db

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)


@router.post("/analyze/{dataset_id}")
def analyze_dataset(
    dataset_id: int,
    user_id: int = Query(..., description="User ID performing the analysis"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform computer vision analysis on dataset images and store results.
    
    This endpoint:
    1. Analyzes images using computer vision
    2. Creates string summaries of CV metrics
    3. Stores results in the database
    4. Returns analysis results
    
    Args:
        dataset_id: ID of the dataset to analyze
        user_id: ID of the user (required for authorization)

    Returns:
        Dict containing analysis results with metrics and summary
    """
    try:
        analysis_service = AnalysisService(db)
        result = analysis_service.analyze_dataset(dataset_id, user_id)

        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 403,
                detail=result.get("error", "Dataset analysis failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/{analysis_id}")
def process_analysis_with_ai(
    analysis_id: int,
    dataset_id: int,
    user_id: int = Query(..., description="User ID requesting AI processing"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process stored analysis results with Gemini AI.
    
    This endpoint:
    1. Retrieves stored CV analysis summary from database
    2. Sends only the string summary to Gemini
    3. Stores AI insights and recommendations
    4. Returns complete analysis with AI results
    
    Args:
        analysis_id: ID of the analysis result to process
        dataset_id: ID of the dataset
        user_id: ID of the user (required for authorization)

    Returns:
        Dict containing AI processing results
    """
    try:
        ai_service = AIService(db)
        result = ai_service.process_analysis_results(dataset_id, user_id, analysis_id)

        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 403,
                detail=result.get("error", "AI processing failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{dataset_id}")
def get_analysis_results(
    dataset_id: int,
    user_id: int = Query(..., description="User ID (must own the dataset)"),
    analysis_id: Optional[int] = Query(None, description="Specific analysis ID (optional)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve analysis results with both CV and AI insights.
    
    Retrieves complete analysis data including:
    - Computer vision metrics (brightness, contrast, blurriness, objects)
    - AI-generated insights and recommendations
    - Class distribution and image formats
    
    Args:
        dataset_id: ID of the dataset
        user_id: ID of the user (must own the dataset)
        analysis_id: Optional specific analysis ID (defaults to latest)

    Returns:
        Dict containing full analysis with CV and AI results
    """
    try:
        ai_service = AIService(db)
        result = ai_service.get_analysis_with_ai_insights(dataset_id, user_id, analysis_id)

        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 403,
                detail=result.get("error", "Failed to retrieve analysis")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/text")
def analyze_text(
    text: str = Query(..., description="Text content to analyze"),
    task: str = Query("analyze", description="Analysis task: analyze, summarize, classify, extract"),
    user_id: Optional[int] = Query(None, description="Optional user ID for tracking"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze custom text content using Gemini AI.
    
    Sends only text (no visual data) to Gemini for analysis.
    
    Args:
        text: Text content to analyze
        task: Type of analysis task
        user_id: Optional user ID for tracking/logging

    Returns:
        Dict containing text analysis results
    """
    try:
        ai_service = AIService(db)
        result = ai_service.analyze_text_content(text, task, user_id)

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Text analysis failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def ai_service_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check AI service health and connection status.
    
    Returns:
        Dict containing service status and configuration
    """
    try:
        ai_service = AIService(db)
        result = ai_service.validate_api_connection()

        return {
            "status": "healthy" if result.get("connected", False) else "unhealthy",
            "service": result.get("service", "Gemini AI"),
            "model": result.get("model", "unknown"),
            "timeout": result.get("timeout", 30),
            "error": result.get("error")
        }

    except Exception as e:
        return {
            "status": "error",
            "service": "Gemini AI",
            "error": str(e)
        }

        raise HTTPException(status_code=500, detail=str(e))