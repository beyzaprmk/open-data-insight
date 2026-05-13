import io
import os
from typing import Optional, Dict, List
import cloudinary
import cloudinary.uploader
import cloudinary.api


class CloudinaryClient:
   

    def __init__(self):
        """Initialize Cloudinary with credentials from environment variables."""
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
        
        # Tüm dosyalar için tek klasör kullan
        self.base_folder = os.getenv("CLOUDINARY_BASE_FOLDER", "datasets")

    def upload_file(
        self,
        file_bytes: bytes,
        file_name: str,
        dataset_id: int,
        resource_type: str = "auto"
    ) -> Dict[str, str]:
        """
        Uploads any type of file (image, text, etc.) to Cloudinary.
        """
        try:
            folder = self.base_folder
            resource_name = f"dataset_{dataset_id}/{file_name.split('.')[0]}"
            
            result = cloudinary.uploader.upload(
                io.BytesIO(file_bytes),
                resource_type=resource_type,
                public_id=resource_name,
                overwrite=True,
                folder=folder,
            )

            return {
                "cloud_id": result.get("public_id"),
                "cloud_url": result.get("secure_url"),
                "file_size": result.get("bytes", 0),
                "file_type": result.get("format", file_name.split('.')[-1]),
                "resource_type": resource_type
            }
        except Exception as e:
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")

    def upload_text_file(
        self,
        file_content: str,
        file_name: str,
        dataset_id: int,
        content_type: str = "labels"
    ) -> Dict[str, str]:

        
        try:
            # Tüm dosyalar base_folder'a yüklenir
            folder = self.base_folder
            
            # Dataset bazlı alt klasör oluştur (folder parametresi zaten klasörü belirtiyor)
            resource_name = f"dataset_{dataset_id}/{file_name.split('.')[0]}"
            
            # Convert string content to bytes for raw upload
            content_bytes = file_content.encode('utf-8')
            
            # Upload as text resource with public access
            result = cloudinary.uploader.upload(
                io.BytesIO(content_bytes),
                resource_type="raw",  # raw resources for non-image files
                public_id=resource_name,
                overwrite=True,
                folder=folder,
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
            # Sadece base_folder'da ara
            resources = cloudinary.api.resources(
                type="upload",
                prefix=f"{self.base_folder}/dataset_{dataset_id}",
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
                    "folder": self.base_folder,
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
