from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from app.integrations.gemini_client import GeminiClient
from app.models.models import AnalysisResult
from app.repositories.dataset_repository import DatasetRepository


class AIService:
    """Service for AI-powered processing of analysis results.
    
    Receives stored analysis results (string summaries from CV analysis).
    Sends only string data to Gemini for AI insights.
    Handles user authorization for dataset access.
    """

    def __init__(self, session: Session):
        """Initialize with database session and AI client."""
        self.session = session
        self.gemini_client = GeminiClient()
        self.dataset_repo = DatasetRepository(session)

    def process_analysis_results(
        self,
        dataset_id: int,
        user_id: int,
        analysis_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process stored analysis results with Gemini AI.
        
        Retrieves CV analysis summaries from the database and sends them
        to Gemini for AI insights. Results are stored back in the database.

        Args:
            dataset_id: ID of the dataset
            user_id: ID of the user requesting (for authorization)
            analysis_id: Optional specific analysis ID to process

        Returns:
            Dict containing AI processing results
        """
        try:
            # Authorization: verify user has access to dataset
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return {
                    "success": False,
                    "error": f"Dataset {dataset_id} not found"
                }

            if dataset.owner_id != user_id:
                return {
                    "success": False,
                    "error": "User does not have access to this dataset"
                }

            # Get the analysis result to process
            if analysis_id:
                analysis = self.session.query(AnalysisResult).filter(
                    AnalysisResult.analysis_id == analysis_id,
                    AnalysisResult.dataset_id == dataset_id
                ).first()
            else:
                # Get the latest analysis result
                analysis = self.session.query(AnalysisResult).filter(
                    AnalysisResult.dataset_id == dataset_id
                ).order_by(AnalysisResult.created_at.desc()).first()

            if not analysis:
                return {
                    "success": False,
                    "error": "No analysis results found for this dataset"
                }

            # Dinamik olarak CV Analiz Özetini (cv_summary) oluştur
            stats = self.dataset_repo.get_dataset_stats(dataset_id)
            
            # Format class distribution into a readable list
            class_dist_str = "No class information available"
            if analysis.class_distribution:
                lines = []
                for class_name, count in analysis.class_distribution.items():
                    lines.append(f"  - {class_name}: {count}")
                class_dist_str = "\n".join(lines)

            cv_summary = f\"\"\"
Computer Vision Analysis Summary for: {dataset.name}

Image Statistics:
- Average brightness: {analysis.brightness_score:.2f}
- Average contrast: {analysis.contrast_score:.2f}
- Average blurriness: {analysis.blurriness_score:.2f}
- Average objects detected: {analysis.avg_object_count:.1f}

Class Distribution:
{class_dist_str}

Dataset Info:
- Total data files: {stats.get('total_data_files', 0)}
- Created: {stats.get('created_at', 'Unknown')}
\"\"\".strip()

            if not cv_summary:
                return {
                    "success": False,
                    "error": "Analysis summary not available"
                }

            # Process with Gemini (send only string data)
            ai_result = self.gemini_client.analyze_text(
                text=cv_summary,
                task="analyze"
            )

            if not ai_result.get("success", False):
                return {
                    "success": False,
                    "error": ai_result.get("error", "AI processing failed"),
                    "analysis_id": analysis.analysis_id
                }

            # Extract insights and recommendations from AI response
            full_analysis = ai_result.get("analysis", "")
            insights = self._extract_insights(full_analysis)
            recommendations = self._extract_recommendations(full_analysis)

            # Not: Bu değerler AnalysisResult tablosunda olmadığından
            # kaydedilmez, sadece API isteğine yanıt olarak döneriz.

            return {
                "success": True,
                "dataset_id": dataset_id,
                "analysis_id": analysis.analysis_id,
                "ai_insights": insights,
                "ai_recommendations": recommendations,
                "model_used": ai_result.get("model", "gemini-1.5-flash"),
                "cv_summary": cv_summary
            }

        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": str(e),
                "dataset_id": dataset_id
            }

    def analyze_text_content(
        self,
        text: str,
        task: str = "analyze",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze text content using Gemini AI.
        
        For analyzing custom text prompts or data.

        Args:
            text: Text content to analyze
            task: Analysis task ('analyze', 'summarize', 'classify', 'extract')
            user_id: Optional user ID for tracking

        Returns:
            Dict containing analysis results
        """
        try:
            result = self.gemini_client.analyze_text(text, task)

            return {
                "success": result.get("success", False),
                "task": task,
                "analysis": result.get("analysis", ""),
                "model": result.get("model", "unknown"),
                "text_length": len(text),
                "user_id": user_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task,
                "user_id": user_id
            }

    def _extract_insights(self, full_analysis: str) -> str:
        """
        Extract key insights from full AI analysis.
        
        Extracts the main findings/insights from the AI response.
        """
        lines = full_analysis.split('\n')
        insights = []
        capture = False
        
        for line in lines:
            lower_line = line.lower()
            if 'insight' in lower_line or 'finding' in lower_line or 'pattern' in lower_line:
                capture = True
            elif 'recommend' in lower_line:
                capture = False
            
            if capture and line.strip():
                insights.append(line.strip())
        
        return '\n'.join(insights) if insights else full_analysis[:500]

    def _extract_recommendations(self, full_analysis: str) -> str:
        """
        Extract recommendations from full AI analysis.
        
        Extracts the recommendations/suggestions from the AI response.
        """
        lines = full_analysis.split('\n')
        recommendations = []
        capture = False
        
        for line in lines:
            lower_line = line.lower()
            if 'recommend' in lower_line or 'suggest' in lower_line or 'improve' in lower_line:
                capture = True
            
            if capture and line.strip():
                recommendations.append(line.strip())
        
        return '\n'.join(recommendations) if recommendations else ""

    def get_analysis_with_ai_insights(
        self,
        dataset_id: int,
        user_id: int,
        analysis_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve analysis result with both CV and AI insights.

        Args:
            dataset_id: ID of the dataset
            user_id: ID of the user requesting (for authorization)
            analysis_id: Optional specific analysis ID

        Returns:
            Dict containing full analysis with insights
        """
        try:
            # Authorization check
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return {"success": False, "error": "Dataset not found"}

            if dataset.owner_id != user_id:
                return {"success": False, "error": "User does not have access to this dataset"}

            # Get analysis
            if analysis_id:
                analysis = self.session.query(AnalysisResult).filter(
                    AnalysisResult.analysis_id == analysis_id,
                    AnalysisResult.dataset_id == dataset_id
                ).first()
            else:
                analysis = self.session.query(AnalysisResult).filter(
                    AnalysisResult.dataset_id == dataset_id
                ).order_by(AnalysisResult.created_at.desc()).first()

            if not analysis:
                return {"success": False, "error": "No analysis results found"}

            return {
                "success": True,
                "analysis_id": analysis.analysis_id,
                "dataset_id": dataset_id,
                "metrics": {
                    "brightness": analysis.brightness_score,
                    "contrast": analysis.contrast_score,
                    "blurriness": analysis.blurriness_score,
                    "avg_objects": analysis.avg_object_count,
                    "class_distribution": analysis.class_distribution
                },
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def validate_api_connection(self) -> Dict[str, Any]:
        """
        Test AI service connection and return status.

        Returns:
            Dict containing connection test results
        """
        try:
            result = self.gemini_client.validate_api_connection()

            return {
                "service": "Gemini AI",
                "connected": result.get("connected", False),
                "model": result.get("model", "unknown"),
                "response": result.get("response", ""),
                "timeout": result.get("timeout", 30)
            }

        except Exception as e:
            return {
                "service": "Gemini AI",
                "connected": False,
                "error": str(e)
            }


    def generate_insights(self, dataset_id: int) -> Dict[str, Any]:
        """
        Generate AI insights for a dataset.

        Args:
            dataset_id: ID of the dataset to analyze

        Returns:
            Dict containing AI-generated insights
        """
        try:
            # Get dataset information
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return {
                    "success": False,
                    "error": f"Dataset {dataset_id} not found"
                }

            # Get dataset statistics
            stats = self.dataset_repo.get_dataset_stats(dataset_id)

            # Create data summary for AI analysis
            data_summary = {
                "dataset_name": dataset.name,
                "description": dataset.description,
                "total_images": stats.get("total_images", 0),
                "total_data_files": stats.get("total_data_files", 0),
                "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
                "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
            }

            # Generate insights using Gemini
            insights_result = self.gemini_client.generate_insights(data_summary)

            return {
                "success": True,
                "dataset_id": dataset_id,
                "dataset_name": dataset.name,
                "insights": insights_result.get("insights", ""),
                "model_used": insights_result.get("model", "unknown"),
                "generated_at": insights_result.get("timestamp", None)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dataset_id": dataset_id
            }

    def analyze_text_content(self, text: str, task: str = "analyze") -> Dict[str, Any]:
        """
        Analyze text content using Gemini AI.

        Args:
            text: Text content to analyze
            task: Analysis task ('analyze', 'summarize', 'classify', 'extract')

        Returns:
            Dict containing analysis results
        """
        try:
            result = self.gemini_client.analyze_text(text, task)

            return {
                "success": result.get("success", False),
                "task": task,
                "analysis": result.get("analysis", ""),
                "model": result.get("model", "unknown"),
                "text_length": len(text)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task
            }

    def classify_dataset_content(self, dataset_id: int) -> Dict[str, Any]:
        """
        Classify and categorize dataset content using AI.

        Args:
            dataset_id: ID of the dataset to classify

        Returns:
            Dict containing classification results
        """
        try:
            # Get dataset data files
            data_files = self.dataset_repo.get_data_files(dataset_id)

            if not data_files:
                return {
                    "success": False,
                    "error": "No data files found in dataset"
                }

            # Analyze first data file as sample
            sample_file = data_files[0]
            # Note: In a real implementation, you'd read the actual file content
            # For now, we'll use a placeholder analysis

            classification_prompt = f"""
            Classify this dataset based on the following information:
            - Dataset ID: {dataset_id}
            - Number of data files: {len(data_files)}
            - File types: {[f.content_type for f in data_files]}

            Provide:
            1. Dataset category (e.g., images, text, mixed)
            2. Potential use cases
            3. Data quality assessment
            """

            result = self.gemini_client.analyze_text(classification_prompt, "classify")

            return {
                "success": result.get("success", False),
                "dataset_id": dataset_id,
                "classification": result.get("analysis", ""),
                "data_files_count": len(data_files),
                "model": result.get("model", "unknown")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dataset_id": dataset_id
            }

    def validate_ai_connection(self) -> Dict[str, Any]:
        """
        Test AI service connection and return status.

        Returns:
            Dict containing connection test results
        """
        try:
            result = self.gemini_client.validate_api_connection()

            return {
                "service": "Gemini AI",
                "connected": result.get("connected", False),
                "model": result.get("model", "unknown"),
                "response": result.get("response", ""),
                "timeout": result.get("timeout", 30)
            }

        except Exception as e:
            return {
                "service": "Gemini AI",
                "connected": False,
                "error": str(e)
            }

