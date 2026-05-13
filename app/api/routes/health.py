from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.database import get_db

router = APIRouter(
    prefix="/api",
    tags=["health"]
)


@router.get("/health")
def health_check() -> dict:
    """Basic liveness probe response."""
    return {
        "status": "ok",
        "service": "OpenDataInsight API"
    }


@router.get("/health/ai")
def ai_health_check(db: Session = Depends(get_db)) -> dict:
    """Check AI service connectivity."""
    try:
        ai_service = AIService(db)
        result = ai_service.validate_ai_connection()

        return {
            "status": "ok" if result.get("connected", False) else "error",
            "service": "AI Service",
            "ai_status": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}"
        )


@router.get("/health/full")
def full_health_check(db: Session = Depends(get_db)) -> dict:
    """Comprehensive health check including all services."""
    health_status = {
        "status": "ok",
        "service": "OpenDataInsight API",
        "checks": {}
    }

    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {"status": "ok"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "error", "error": str(e)}
        health_status["status"] = "error"

    # AI service check
    try:
        ai_service = AIService(db)
        ai_result = ai_service.validate_ai_connection()
        health_status["checks"]["ai_service"] = {
            "status": "ok" if ai_result.get("connected", False) else "error",
            "model": ai_result.get("model", "unknown")
        }
        if not ai_result.get("connected", False):
            health_status["status"] = "error"
    except Exception as e:
        health_status["checks"]["ai_service"] = {"status": "error", "error": str(e)}
        health_status["status"] = "error"

    return health_status

