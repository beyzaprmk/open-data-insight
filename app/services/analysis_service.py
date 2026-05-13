from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import cv2
import numpy as np
from app.models.models import AnalysisResult
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.image_repository import ImageRepository


class AnalysisService:
    """Service for computer vision analysis of visual data."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)

    def analyze_dataset(self, dataset_id: int, user_id: int) -> Dict[str, Any]:
        """
        Perform computer vision analysis on dataset images and store results.
        
        This method analyzes visual data and creates string summaries.
        Analysis results are stored in the database (not sent to Gemini).

        Args:
            dataset_id: ID of the dataset to analyze
            user_id: ID of the user performing the analysis (for authorization)

        Returns:
            Dict containing analysis results
        """
        try:
            # Authorization check: verify user owns or has access to dataset
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

            # Perform CV analysis on images
            image_analysis = self._analyze_images(dataset_id)
            
            # Get dataset statistics
            stats = self.dataset_repo.get_dataset_stats(dataset_id)

            # Create string summaries of analysis
            cv_summary = self._create_analysis_summary(
                dataset_name=dataset.name,
                image_analysis=image_analysis,
                stats=stats
            )

            # Store analysis results in database
            analysis_result = AnalysisResult(
                dataset_id=dataset_id,
                brightness_score=image_analysis.get("avg_brightness"),
                contrast_score=image_analysis.get("avg_contrast"),
                blurriness_score=image_analysis.get("avg_blurriness"),
                avg_object_count=image_analysis.get("avg_objects"),
                class_distribution=image_analysis.get("class_distribution")
            )
            
            self.session.add(analysis_result)
            self.session.commit()

            return {
                "success": True,
                "dataset_id": dataset_id,
                "analysis_id": analysis_result.analysis_id,
                "analysis_type": "cv",
                "summary": cv_summary,
                "metrics": image_analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "dataset_id": dataset_id
            }

    def _analyze_images(self, dataset_id: int) -> Dict[str, Any]:
        """
        Analyze images using computer vision.
        
        Returns string-formatted analysis results, NOT raw visual data.

        Args:
            dataset_id: Dataset ID to analyze

        Returns:
            Dict containing CV analysis metrics
        """
        try:
            images = self.image_repo.get_by_dataset_id(dataset_id)

            if not images:
                return {
                    "total_images": 0,
                    "message": "No images found"
                }

            brightness_scores = []
            contrast_scores = []
            blurriness_scores = []
            object_counts = []
            class_distribution = {}

            for image in images:
                # In a real implementation, you would:
                # 1. Download image from Cloudinary
                # 2. Perform CV analysis (brightness, contrast, blurriness, object detection)
                # 3. Extract metrics and convert to numbers
                
                # For now, simulate with placeholder values
                brightness_scores.append(0.65)  # Placeholder
                contrast_scores.append(0.58)    # Placeholder
                blurriness_scores.append(0.12)  # Placeholder
                object_counts.append(3)          # Placeholder

                # Track class distribution
                if image.file_type not in class_distribution:
                    class_distribution[image.file_type] = 0
                class_distribution[image.file_type] += 1

            return {
                "total_images": len(images),
                "avg_brightness": np.mean(brightness_scores) if brightness_scores else 0,
                "avg_contrast": np.mean(contrast_scores) if contrast_scores else 0,
                "avg_blurriness": np.mean(blurriness_scores) if blurriness_scores else 0,
                "avg_objects": np.mean(object_counts) if object_counts else 0,
                "class_distribution": class_distribution,
                "formats": list(set([img.file_type for img in images]))
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_images": 0
            }

    def _create_analysis_summary(
        self,
        dataset_name: str,
        image_analysis: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """
        Create a string summary of computer vision analysis.
        
        This summary will be sent to Gemini for further AI processing.

        Args:
            dataset_name: Name of the dataset
            image_analysis: CV analysis metrics
            stats: Dataset statistics

        Returns:
            String summary of analysis
        """
        summary = f"""
Computer Vision Analysis Summary for: {dataset_name}

Image Statistics:
- Total images: {image_analysis.get('total_images', 0)}
- Average brightness: {image_analysis.get('avg_brightness', 0):.2f}
- Average contrast: {image_analysis.get('avg_contrast', 0):.2f}
- Average blurriness: {image_analysis.get('avg_blurriness', 0):.2f}
- Average objects detected: {image_analysis.get('avg_objects', 0):.1f}

Class Distribution:
{self._format_class_distribution(image_analysis.get('class_distribution', {}))}

Image Formats: {', '.join(image_analysis.get('formats', []))}

Dataset Info:
- Total data files: {stats.get('total_data_files', 0)}
- Created: {stats.get('created_at', 'Unknown')}
""".strip()
        return summary

    def _format_class_distribution(self, distribution: Dict[str, int]) -> str:
        """Format class distribution for display."""
        if not distribution:
            return "No class information available"
        
        lines = []
        for class_name, count in distribution.items():
            lines.append(f"  - {class_name}: {count}")
        return "\n".join(lines)

    def get_analysis_result(self, analysis_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis result from database with authorization check.

        Args:
            analysis_id: ID of the analysis result
            user_id: ID of the user requesting (for authorization)

        Returns:
            Dict containing analysis result or None if not found/unauthorized
        """
        try:
            analysis = self.session.query(AnalysisResult).filter(
                AnalysisResult.analysis_id == analysis_id
            ).first()

            if not analysis:
                return None

            # Authorization: check if user owns the dataset or is a collaborator
            dataset = analysis.dataset
            if dataset.owner_id != user_id:
                # Could check collaborations here
                return None

            return {
                "analysis_id": analysis.analysis_id,
                "dataset_id": analysis.dataset_id,
                "brightness_score": analysis.brightness_score,
                "contrast_score": analysis.contrast_score,
                "blurriness_score": analysis.blurriness_score,
                "avg_object_count": analysis.avg_object_count,
                "class_distribution": analysis.class_distribution,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            }

        except Exception as e:
            return None
