from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from app.models.models import Dataset, DataFile, User, Label


class DatasetRepository:
    """Repository for Dataset data access operations."""

    def __init__(self, session: Session):
        """Initialize with a SQLAlchemy session."""
        self.session = session

    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dataset]:
        """Get a dataset by ID."""
        return self.session.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()

    def get_datasets_by_owner(self, owner_id: int) -> List[Dataset]:
        """Get all datasets owned by a user."""
        return self.session.query(Dataset).filter(Dataset.owner_id == owner_id).all()

    def get_public_datasets(self) -> List[Dataset]:
        """Get all public datasets."""
        return self.session.query(Dataset).filter(Dataset.visibility == True).all()

    def create_dataset(
        self,
        owner_id: int,
        name: str,
        description: Optional[str] = None,
        visibility: bool = True,
        is_labeled: bool = False
    ) -> Dataset:
        """Create a new dataset."""
        dataset = Dataset(
            owner_id=owner_id,
            name=name,
            description=description,
            visibility=visibility,
            is_labeled=is_labeled
        )
        self.session.add(dataset)
        self.session.commit()
        return dataset

    def update_dataset(
        self,
        dataset_id: int,
        **kwargs
    ) -> Optional[Dataset]:
        """Update a dataset."""
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            return None
        
        for key, value in kwargs.items():
            if hasattr(dataset, key):
                setattr(dataset, key, value)
        
        dataset.updated_at = datetime.utcnow()
        self.session.commit()
        return dataset

    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset."""
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            return False
        
        self.session.delete(dataset)
        self.session.commit()
        return True

    def get_dataset_file_count(self, dataset_id: int) -> int:
        """Get count of files in a dataset."""
        return self.session.query(DataFile).filter(DataFile.dataset_id == dataset_id).count()

    def get_public_datasets_filtered(
        self,
        search_keyword: Optional[str] = None,
        tag_types: Optional[List[str]] = None,
        data_status: Optional[str] = None
    ) -> List[Dataset]:
        """
        Get public datasets with advanced filtering.
        
        Args:
            search_keyword: Filter by dataset name (partial match)
            tag_types: Filter by label names (e.g., ['Cat', 'Dog', 'Human'])
            data_status: Filter by data status ('Tagged' for is_labeled=True, 'Raw' for is_labeled=False)
        
        Returns:
            List of filtered Dataset objects
        """
        query = self.session.query(Dataset).filter(Dataset.visibility == True)
        
        # Filter by search keyword (dataset name)
        if search_keyword and search_keyword.strip():
            query = query.filter(Dataset.name.ilike(f"%{search_keyword}%"))
        
        # Filter by data status (Tagged/Raw)
        if data_status:
            if data_status.lower() == "tagged":
                query = query.filter(Dataset.is_labeled == True)
            elif data_status.lower() == "raw":
                query = query.filter(Dataset.is_labeled == False)
        
        # Filter by tag types (labels)
        if tag_types and len(tag_types) > 0:
            query = query.join(Label).filter(Label.label_name.in_(tag_types)).distinct()
        
        return query.all()
