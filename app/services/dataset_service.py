from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Service for managing datasets."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
        self.repository = DatasetRepository(session)

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
