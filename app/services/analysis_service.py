from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import cv2
import numpy as np
from app.models.models import AnalysisResult
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.image_repository import ImageRepository
from app.integrations.opencv_adapter import OpenCVAdapter
from app.database import SessionLocal


class AnalysisService:
    """Service for computer vision analysis of visual data."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)

    def start_analysis_background(self, dataset_id: int, user_id: int, background_tasks: Any) -> Dict[str, Any]:
        """
        Background task formatında analizi başlatır. FastAPI'den 202 dönülmesi için
        sadece veritabanında boş kayıt açar ve asıl işi background'a atar.
        """
        try:
            # Authorization check
            dataset = self.dataset_repo.get_by_id(dataset_id)
            if not dataset:
                return {"success": False, "error": f"Dataset {dataset_id} not found"}

            if dataset.owner_id != user_id:
                return {"success": False, "error": "User does not have access to this dataset"}

            # Başlangıç kaydı (status='processing') oluşturuluyor
            analysis_result = AnalysisResult(
                dataset_id=dataset_id,
                status="processing"
            )
            self.session.add(analysis_result)
            self.session.commit()
            self.session.refresh(analysis_result)

            # Ağır işi background asenkron formata gönder (fire and forget)
            background_tasks.add_task(
                self.perform_heavy_cv_analysis,
                dataset_id=dataset_id,
                analysis_id=analysis_result.analysis_id
            )

            return {
                "success": True,
                "message": "Analysis started in background.",
                "analysis_id": analysis_result.analysis_id,
                "dataset_id": dataset_id,
                "status": "processing"
            }

        except Exception as e:
            return {"success": False, "error": str(e), "dataset_id": dataset_id}

    def perform_heavy_cv_analysis(self, dataset_id: int, analysis_id: int):
        """
        Arka planda (BackgroundTasks) çalışacak asıl uzun soluklu metod.
        Cloudinary üzerinden imaj URL'lerini alıp Engine (OpenCVAdapter) ile işler.
        Oturum yaşam döngüsü sorununu önlemek için yepyeni bir DB Session açar.
        """
        db: Session = SessionLocal()
        try:
            # Resimleri Çek
            image_repo = ImageRepository(db)
            images = image_repo.get_by_dataset_id(dataset_id)
            
            # URL listesi oluştur
            image_urls = [img.cloud_url for img in images] if images else []

            # Analiz Motoruna Delege Et (Şu an gelişime başlatılmadı, sadece adapter devrede)
            cv_results = OpenCVAdapter.process_images(image_urls)

            # DB'de Sonucu Güncelle
            analysis = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id).first()
            if analysis:
                analysis.status = "completed"
                analysis.brightness_score = cv_results.get("avg_brightness")
                analysis.contrast_score = cv_results.get("avg_contrast")
                analysis.blurriness_score = cv_results.get("avg_blurriness")
                analysis.avg_object_count = cv_results.get("avg_objects")
                analysis.class_distribution = cv_results.get("class_distribution")
                db.commit()

        except Exception as e:
            db.rollback()
            # Hata oluştuysa DB'ye kaydet
            analysis = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                db.commit()
        finally:
            db.close()

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
