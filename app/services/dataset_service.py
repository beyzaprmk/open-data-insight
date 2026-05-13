from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.image_repository import ImageRepository


class DatasetService:
    """Service for managing datasets."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
        self.repository = DatasetRepository(session)
        self.image_repository = ImageRepository(session)

    def create_dataset(
        self,
        owner_id: int,
        name: str,
        description: Optional[str] = None,
        visibility: bool = True
    ) -> Dict:
        """Create a new dataset."""
        dataset = self.repository.create_dataset(
            owner_id=owner_id,
            name=name,
            description=description,
            visibility=visibility
        )
        return self._dataset_to_dict(dataset)

    def get_dataset(self, dataset_id: int) -> Optional[Dict]:
        """Get dataset by ID."""
        dataset = self.repository.get_dataset_by_id(dataset_id)
        return self._dataset_to_dict(dataset) if dataset else None

    def get_user_datasets(self, user_id: int) -> List[Dict]:
        """Get all datasets owned by a user."""
        datasets = self.repository.get_datasets_by_owner(user_id)
        return [self._dataset_to_dict(d) for d in datasets]

    def get_public_datasets(self) -> List[Dict]:
        """Get all public datasets."""
        datasets = self.repository.get_public_datasets()
        return [self._dataset_to_dict(d) for d in datasets]

    def get_public_datasets_with_images(self) -> List[Dict]:
        """Get all public datasets with their images from Cloudinary."""
        datasets = self.repository.get_public_datasets()
        result = []
        for dataset in datasets:
            dataset_dict = self._dataset_to_dict(dataset)
            # Get images for this dataset
            images = self.image_repository.get_by_dataset_id(dataset.dataset_id)
            dataset_dict["images"] = [
                {
                    "image_id": img.image_id,
                    "file_name": img.file_name,
                    "cloud_path": img.cloud_path,
                    "file_type": img.file_type,
                    "uploaded_at": img.uploaded_at.isoformat(),
                }
                for img in images
            ]
            result.append(dataset_dict)
        return result

    def get_public_datasets_filtered(
        self,
        search_keyword: Optional[str] = None,
        tag_types: Optional[List[str]] = None,
        data_status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get public datasets with advanced filtering and their images.
        
        Args:
            search_keyword: Filter by dataset name (partial match)
            tag_types: Filter by label names (e.g., ['Cat', 'Dog', 'Human'])
            data_status: Filter by data status ('Tagged' for is_labeled=True, 'Raw' for is_labeled=False)
        
        Returns:
            List of filtered datasets with their images
        """
        datasets = self.repository.get_public_datasets_filtered(
            search_keyword=search_keyword,
            tag_types=tag_types,
            data_status=data_status
        )
        result = []
        for dataset in datasets:
            dataset_dict = self._dataset_to_dict(dataset)
            # Get images for this dataset
            images = self.image_repository.get_by_dataset_id(dataset.dataset_id)
            dataset_dict["images"] = [
                {
                    "image_id": img.image_id,
                    "file_name": img.file_name,
                    "cloud_path": img.cloud_path,
                    "file_type": img.file_type,
                    "uploaded_at": img.uploaded_at.isoformat(),
                }
                for img in images
            ]
            result.append(dataset_dict)
        return result

    def update_dataset(
        self,
        dataset_id: int,
        **kwargs
    ) -> Optional[Dict]:
        """Update a dataset."""
        dataset = self.repository.update_dataset(dataset_id, **kwargs)
        return self._dataset_to_dict(dataset) if dataset else None

    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset."""
        return self.repository.delete_dataset(dataset_id)

    @staticmethod
    def _dataset_to_dict(dataset) -> Dict:
        """Convert dataset model to dictionary."""
        return {
            "dataset_id": dataset.dataset_id,
            "owner_id": dataset.owner_id,
            "name": dataset.name,
            "description": dataset.description,
            "visibility": dataset.visibility,
            "is_labeled": dataset.is_labeled,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }
