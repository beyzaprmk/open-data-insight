from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import DataFile, DatasetImage


class ImageRepository:
    """Repository for DatasetImage and DataFile data access operations."""

    def __init__(self, session: Session):
        """Initialize with a SQLAlchemy session."""
        self.session = session


class DataFileRepository:
    """Repository for DataFile (text files with image data and labels) operations."""

    def __init__(self, session: Session):
        """Initialize with a SQLAlchemy session."""
        self.session = session

    def create_data_file(
        self,
        dataset_id: int,
        uploaded_by: int,
        file_name: str,
        file_type: str,
        file_size: int,
        cloud_id: str,
        cloud_url: str,
        content_type: str = "labels",
        description: Optional[str] = None,
        is_public: bool = True
    ) -> DataFile:
        """Create a new data file record."""
        data_file = DataFile(
            dataset_id=dataset_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            cloud_id=cloud_id,
            cloud_url=cloud_url,
            content_type=content_type,
            description=description,
            is_public=is_public
        )
        self.session.add(data_file)
        self.session.commit()
        return data_file

    def get_data_file_by_id(self, file_id: int) -> Optional[DataFile]:
        """Get a data file by ID."""
        return self.session.query(DataFile).filter(DataFile.file_id == file_id).first()

    def get_data_file_by_cloud_id(self, cloud_id: str) -> Optional[DataFile]:
        """Get a data file by Cloudinary ID."""
        return self.session.query(DataFile).filter(DataFile.cloud_id == cloud_id).first()

    def get_files_by_dataset(self, dataset_id: int) -> List[DataFile]:
        """Get all files for a dataset."""
        return self.session.query(DataFile).filter(
            DataFile.dataset_id == dataset_id
        ).order_by(DataFile.created_at.desc()).all()

    def get_files_by_user(self, user_id: int) -> List[DataFile]:
        """Get all files uploaded by a user."""
        return self.session.query(DataFile).filter(
            DataFile.uploaded_by == user_id
        ).order_by(DataFile.created_at.desc()).all()

    def get_public_files(self, dataset_id: Optional[int] = None) -> List[DataFile]:
        """Get all public files, optionally filtered by dataset."""
        query = self.session.query(DataFile).filter(DataFile.is_public == True)
        if dataset_id:
            query = query.filter(DataFile.dataset_id == dataset_id)
        return query.order_by(DataFile.created_at.desc()).all()

    def get_files_by_content_type(
        self,
        content_type: str,
        dataset_id: Optional[int] = None
    ) -> List[DataFile]:
        """Get files by content type, optionally filtered by dataset."""
        query = self.session.query(DataFile).filter(
            DataFile.content_type == content_type
        )
        if dataset_id:
            query = query.filter(DataFile.dataset_id == dataset_id)
        return query.order_by(DataFile.created_at.desc()).all()

    def update_data_file(
        self,
        file_id: int,
        **kwargs
    ) -> Optional[DataFile]:
        """Update a data file."""
        data_file = self.get_data_file_by_id(file_id)
        if not data_file:
            return None
        
        for key, value in kwargs.items():
            if hasattr(data_file, key):
                setattr(data_file, key, value)
        
        data_file.updated_at = datetime.utcnow()
        self.session.commit()
        return data_file

    def delete_data_file(self, file_id: int) -> bool:
        """Delete a data file record."""
        data_file = self.get_data_file_by_id(file_id)
        if not data_file:
            return False
        
        self.session.delete(data_file)
        self.session.commit()
        return True

    def count_dataset_files(self, dataset_id: int) -> int:
        """Count total files in a dataset."""
        return self.session.query(DataFile).filter(
            DataFile.dataset_id == dataset_id
        ).count()

    def count_user_files(self, user_id: int) -> int:
        """Count total files uploaded by a user."""
        return self.session.query(DataFile).filter(
            DataFile.uploaded_by == user_id
        ).count()
