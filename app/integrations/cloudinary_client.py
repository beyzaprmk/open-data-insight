import os
from typing import Optional, Dict, List
import cloudinary
import cloudinary.uploader
import cloudinary.api


class CloudinaryClient:
    """
    Client for managing file uploads/downloads with Cloudinary.
    Handles text files containing image data and labels.
    All files are stored as public resources.
    """

    def __init__(self):
        """Initialize Cloudinary with credentials from environment variables."""
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )

    def upload_text_file(
        self,
        file_content: str,
        file_name: str,
        dataset_id: int,
        content_type: str = "labels"
    ) -> Dict[str, str]:
        """
        Upload a text file containing image data or labels to Cloudinary.

        Args:
            file_content: The text content to upload
            file_name: Original file name
            dataset_id: Dataset ID for organization
            content_type: Type of content ('image_data', 'labels', 'mixed')

        Returns:
            Dict containing cloud_id, cloud_url, file_size, file_type

        Raises:
            Exception: If upload fails
        """
        try:
            # Create a resource name based on dataset and file
            resource_name = f"dataset_{dataset_id}/{file_name.split('.')[0]}"
            
            # Upload as text resource with public access
            result = cloudinary.uploader.upload(
                file_content,
                resource_type="raw",  # raw resources for non-image files
                public_id=resource_name,
                access_control=[
                    {"access_type": "token", "start": None, "end": None}
                ],  # allow public access
                overwrite=True,
                folder="datasets",
            )

            return {
                "cloud_id": result.get("public_id"),
                "cloud_url": result.get("secure_url"),
                "file_size": result.get("bytes", 0),
                "file_type": result.get("format", "txt"),
            }
        except Exception as e:
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")

    def delete_file(self, cloud_id: str) -> bool:
        """
        Delete a file from Cloudinary.

        Args:
            cloud_id: Public ID of the resource to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            result = cloudinary.uploader.destroy(
                cloud_id,
                resource_type="raw"
            )
            return result.get("result") == "ok"
        except Exception as e:
            print(f"Failed to delete file from Cloudinary: {str(e)}")
            return False

    def list_files(self, dataset_id: int) -> List[Dict]:
        """
        List all files for a specific dataset.

        Args:
            dataset_id: Dataset ID to filter files

        Returns:
            List of file metadata dictionaries
        """
        try:
            resources = cloudinary.api.resources(
                type="upload",
                prefix=f"datasets/dataset_{dataset_id}",
                max_results=500
            )
            
            files = []
            for resource in resources.get("resources", []):
                files.append({
                    "cloud_id": resource.get("public_id"),
                    "file_name": resource.get("public_id").split("/")[-1],
                    "cloud_url": resource.get("secure_url"),
                    "file_size": resource.get("bytes", 0),
                    "created_at": resource.get("created_at"),
                })
            
            return files
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []

    def get_file_url(self, cloud_id: str) -> str:
        """
        Get the public URL for a file.

        Args:
            cloud_id: Public ID of the resource

        Returns:
            Public URL of the file
        """
        return cloudinary.utils.cloudinary_url(cloud_id)[0]

    def download_file(self, cloud_id: str) -> Optional[str]:
        """
        Download file content from Cloudinary.

        Args:
            cloud_id: Public ID of the resource

        Returns:
            File content as string, or None if failed
        """
        try:
            url = self.get_file_url(cloud_id)
            import requests
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Failed to download file: {str(e)}")
            return None

    def get_file_metadata(self, cloud_id: str) -> Optional[Dict]:
        """
        Get metadata for a file.

        Args:
            cloud_id: Public ID of the resource

        Returns:
            File metadata dictionary or None if not found
        """
        try:
            resource = cloudinary.api.resource(
                cloud_id,
                resource_type="raw"
            )
            return {
                "cloud_id": resource.get("public_id"),
                "file_size": resource.get("bytes", 0),
                "file_type": resource.get("format"),
                "created_at": resource.get("created_at"),
                "url": resource.get("secure_url"),
            }
        except Exception as e:
            print(f"Failed to get file metadata: {str(e)}")
            return None
