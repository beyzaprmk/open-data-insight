from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.integrations.cloudinary_client import CloudinaryClient
from app.repositories.image_repository import DataFileRepository
from app.models.models import DataFile


class DataFileService:
    """Service for managing data files (text files with image data and labels)."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
        self.cloudinary_client = CloudinaryClient()
        self.repository = DataFileRepository(session)

    def upload_file(
        self,
        dataset_id: int,
        user_id: int,
        file_name: str,
        file_content: str,
        content_type: str = "labels",
        description: Optional[str] = None,
        is_public: bool = True
    ) -> Dict:
        """
        Upload a text file with image data or labels to Cloudinary and save metadata.

        Args:
            dataset_id: Dataset ID
            user_id: User ID of uploader
            file_name: File name
            file_content: Text content of the file
            content_type: Type of content ('image_data', 'labels', 'mixed')
            description: Optional description
            is_public: Whether file is public (default True)

        Returns:
            Dictionary with file metadata and URLs

        Raises:
            Exception: If upload fails
        """
        try:
            # Upload to Cloudinary
            cloud_info = self.cloudinary_client.upload_text_file(
                file_content=file_content,
                file_name=file_name,
                dataset_id=dataset_id,
                content_type=content_type
            )

            # Save metadata to database
            file_type = file_name.split(".")[-1] if "." in file_name else "txt"
            data_file = self.repository.create_data_file(
                dataset_id=dataset_id,
                uploaded_by=user_id,
                file_name=file_name,
                file_type=file_type,
                file_size=cloud_info.get("file_size", 0),
                cloud_id=cloud_info.get("cloud_id"),
                cloud_url=cloud_info.get("cloud_url"),
                content_type=content_type,
                description=description,
                is_public=is_public
            )

            return {
                "file_id": data_file.file_id,
                "file_name": data_file.file_name,
                "cloud_url": data_file.cloud_url,
                "file_size": data_file.file_size,
                "content_type": data_file.content_type,
                "created_at": data_file.created_at.isoformat(),
                "is_public": data_file.is_public
            }
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def delete_file(self, file_id: int, user_id: int) -> bool:
        """
        Delete a file from Cloudinary and database.

        Args:
            file_id: File ID to delete
            user_id: User ID (for permission check)

        Returns:
            True if successful, False otherwise

        Raises:
            PermissionError: If user doesn't own the file
        """
        data_file = self.repository.get_data_file_by_id(file_id)
        if not data_file:
            return False

        # Check if user has permission to delete
        if data_file.uploaded_by != user_id:
            raise PermissionError("User can only delete their own files")

        # Delete from Cloudinary
        success = self.cloudinary_client.delete_file(data_file.cloud_id)
        if success:
            # Delete from database
            return self.repository.delete_data_file(file_id)
        
        return False

    def get_file(self, file_id: int) -> Optional[Dict]:
        """
        Get file metadata.

        Args:
            file_id: File ID

        Returns:
            File metadata dictionary or None
        """
        data_file = self.repository.get_data_file_by_id(file_id)
        if not data_file:
            return None

        return self._file_to_dict(data_file)

    def get_dataset_files(self, dataset_id: int) -> List[Dict]:
        """
        Get all files for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of file metadata dictionaries
        """
        files = self.repository.get_files_by_dataset(dataset_id)
        return [self._file_to_dict(f) for f in files]

    def get_user_files(self, user_id: int) -> List[Dict]:
        """
        Get all files uploaded by a user.

        Args:
            user_id: User ID

        Returns:
            List of file metadata dictionaries
        """
        files = self.repository.get_files_by_user(user_id)
        return [self._file_to_dict(f) for f in files]

    def get_public_files(self, dataset_id: Optional[int] = None) -> List[Dict]:
        """
        Get all public files, optionally filtered by dataset.

        Args:
            dataset_id: Optional dataset ID to filter

        Returns:
            List of public file metadata dictionaries
        """
        files = self.repository.get_public_files(dataset_id)
        return [self._file_to_dict(f) for f in files]

    def get_files_by_content_type(
        self,
        content_type: str,
        dataset_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get files by content type.

        Args:
            content_type: Content type ('image_data', 'labels', 'mixed')
            dataset_id: Optional dataset ID to filter

        Returns:
            List of file metadata dictionaries
        """
        files = self.repository.get_files_by_content_type(content_type, dataset_id)
        return [self._file_to_dict(f) for f in files]

    def download_file(self, file_id: int) -> Optional[str]:
        """
        Download file content.

        Args:
            file_id: File ID

        Returns:
            File content as string or None if failed
        """
        data_file = self.repository.get_data_file_by_id(file_id)
        if not data_file:
            return None

        return self.cloudinary_client.download_file(data_file.cloud_id)

    def get_file_stats(self, dataset_id: int) -> Dict:
        """
        Get statistics for files in a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dictionary with file statistics
        """
        files = self.repository.get_files_by_dataset(dataset_id)
        
        stats = {
            "total_files": len(files),
            "total_size_bytes": sum(f.file_size for f in files),
            "by_content_type": {},
            "by_uploader": {},
            "public_count": sum(1 for f in files if f.is_public),
        }

        # Count by content type
        for file in files:
            content_type = file.content_type
            stats["by_content_type"][content_type] = stats["by_content_type"].get(content_type, 0) + 1

        # Count by uploader
        for file in files:
            uploader_id = file.uploaded_by
            stats["by_uploader"][uploader_id] = stats["by_uploader"].get(uploader_id, 0) + 1

        return stats

    def update_file_description(
        self,
        file_id: int,
        description: str,
        user_id: int
    ) -> Optional[Dict]:
        """
        Update file description.

        Args:
            file_id: File ID
            description: New description
            user_id: User ID (for permission check)

        Returns:
            Updated file metadata or None

        Raises:
            PermissionError: If user doesn't own the file
        """
        data_file = self.repository.get_data_file_by_id(file_id)
        if not data_file:
            return None

        # Check if user has permission
        if data_file.uploaded_by != user_id:
            raise PermissionError("User can only update their own files")

        updated_file = self.repository.update_data_file(
            file_id,
            description=description
        )
        
        return self._file_to_dict(updated_file) if updated_file else None

    def toggle_file_visibility(
        self,
        file_id: int,
        is_public: bool,
        user_id: int
    ) -> Optional[Dict]:
        """
        Toggle file visibility.

        Args:
            file_id: File ID
            is_public: New visibility state
            user_id: User ID (for permission check)

        Returns:
            Updated file metadata or None

        Raises:
            PermissionError: If user doesn't own the file
        """
        data_file = self.repository.get_data_file_by_id(file_id)
        if not data_file:
            return None

        # Check if user has permission
        if data_file.uploaded_by != user_id:
            raise PermissionError("User can only modify their own files")

        updated_file = self.repository.update_data_file(
            file_id,
            is_public=is_public
        )
        
        return self._file_to_dict(updated_file) if updated_file else None

    @staticmethod
    def _file_to_dict(data_file: DataFile) -> Dict:
        """Convert DataFile model to dictionary."""
        return {
            "file_id": data_file.file_id,
            "dataset_id": data_file.dataset_id,
            "uploaded_by": data_file.uploaded_by,
            "file_name": data_file.file_name,
            "file_type": data_file.file_type,
            "file_size": data_file.file_size,
            "cloud_id": data_file.cloud_id,
            "cloud_url": data_file.cloud_url,
            "content_type": data_file.content_type,
            "description": data_file.description,
            "is_public": data_file.is_public,
            "created_at": data_file.created_at.isoformat(),
            "updated_at": data_file.updated_at.isoformat(),
        }
