from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.data_file_service import DataFileService


# Request/Response models
class FileUploadRequest(BaseModel):
    content: str
    content_type: str = "labels"  # 'image_data', 'labels', 'mixed'
    description: Optional[str] = None
    is_public: bool = True


class FileUploadResponse(BaseModel):
    file_id: int
    file_name: str
    cloud_url: str
    file_size: int
    content_type: str
    created_at: str
    is_public: bool


class FileMetadataResponse(BaseModel):
    file_id: int
    dataset_id: int
    uploaded_by: int
    file_name: str
    file_type: str
    file_size: int
    cloud_url: str
    content_type: str
    description: Optional[str]
    is_public: bool
    created_at: str
    updated_at: str


class FileStatsResponse(BaseModel):
    total_files: int
    total_size_bytes: int
    public_count: int
    by_content_type: dict
    by_uploader: dict


# Create router
router = APIRouter(
    prefix="/api/datasets",
    tags=["data-files"]
)


# Dependency to get database session (placeholder - replace with actual DB dependency)
def get_db():
    # This should be replaced with actual database session logic
    pass


# Endpoints
@router.post(
    "/{dataset_id}/files",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload data file",
    description="Upload a text file containing image data or labels to a dataset"
)
def upload_file(
    dataset_id: int,
    file_name: str,
    request: FileUploadRequest,
    user_id: int = Query(..., description="User ID of uploader"),
    session: Session = Depends(get_db)
):
    """
    Upload a text file with image data or labels.
    
    - **dataset_id**: Dataset ID to upload to
    - **file_name**: Name of the file
    - **content**: Text content of the file
    - **content_type**: Type of content ('image_data', 'labels', 'mixed')
    - **description**: Optional file description
    - **is_public**: Whether file is publicly accessible (default: true)
    """
    try:
        service = DataFileService(session)
        result = service.upload_file(
            dataset_id=dataset_id,
            user_id=user_id,
            file_name=file_name,
            file_content=request.content,
            content_type=request.content_type,
            description=request.description,
            is_public=request.is_public
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{dataset_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete data file",
    description="Delete a file from Cloudinary and database"
)
def delete_file(
    dataset_id: int,
    file_id: int,
    user_id: int = Query(..., description="User ID"),
    session: Session = Depends(get_db)
):
    """
    Delete a file. Only the file owner can delete their own files.
    
    - **dataset_id**: Dataset ID
    - **file_id**: File ID to delete
    - **user_id**: User ID (must match uploader)
    """
    try:
        service = DataFileService(session)
        success = service.delete_file(file_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{dataset_id}/files/{file_id}",
    response_model=FileMetadataResponse,
    summary="Get file metadata",
    description="Retrieve metadata for a specific file"
)
def get_file(
    dataset_id: int,
    file_id: int,
    session: Session = Depends(get_db)
):
    """Get file metadata by ID."""
    service = DataFileService(session)
    file_data = service.get_file(file_id)
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return file_data


@router.get(
    "/{dataset_id}/files",
    response_model=list[FileMetadataResponse],
    summary="List dataset files",
    description="Get all files for a dataset"
)
def list_dataset_files(
    dataset_id: int,
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    public_only: bool = Query(False, description="Show only public files"),
    session: Session = Depends(get_db)
):
    """
    List all files in a dataset.
    
    - **dataset_id**: Dataset ID
    - **content_type**: Optional filter by content type
    - **public_only**: If true, show only public files
    """
    service = DataFileService(session)
    
    if public_only:
        files = service.get_public_files(dataset_id)
    elif content_type:
        files = service.get_files_by_content_type(content_type, dataset_id)
    else:
        files = service.get_dataset_files(dataset_id)
    
    return files


@router.get(
    "/{dataset_id}/files/stats",
    response_model=FileStatsResponse,
    summary="Get file statistics",
    description="Get statistics about files in a dataset"
)
def get_file_stats(
    dataset_id: int,
    session: Session = Depends(get_db)
):
    """Get file statistics for a dataset."""
    service = DataFileService(session)
    stats = service.get_file_stats(dataset_id)
    return stats


@router.get(
    "/files/download/{file_id}",
    summary="Download file",
    description="Download file content"
)
def download_file(
    file_id: int,
    session: Session = Depends(get_db)
):
    """
    Download file content.
    
    - **file_id**: File ID to download
    """
    service = DataFileService(session)
    content = service.download_file(file_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or download failed"
        )
    return {
        "content": content,
        "file_id": file_id
    }


@router.put(
    "/{dataset_id}/files/{file_id}",
    response_model=FileMetadataResponse,
    summary="Update file metadata",
    description="Update file description and visibility"
)
def update_file(
    dataset_id: int,
    file_id: int,
    description: Optional[str] = Query(None, description="New description"),
    is_public: Optional[bool] = Query(None, description="New visibility state"),
    user_id: int = Query(..., description="User ID"),
    session: Session = Depends(get_db)
):
    """
    Update file metadata. Only the file owner can update their files.
    
    - **dataset_id**: Dataset ID
    - **file_id**: File ID to update
    - **description**: New description
    - **is_public**: New visibility state
    """
    try:
        service = DataFileService(session)
        
        file_data = None
        if description is not None:
            file_data = service.update_file_description(file_id, description, user_id)
        if is_public is not None:
            file_data = service.toggle_file_visibility(file_id, is_public, user_id)
        
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return file_data
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/user/{user_id}/files",
    response_model=list[FileMetadataResponse],
    summary="Get user files",
    description="Get all files uploaded by a user"
)
def get_user_files(
    user_id: int,
    session: Session = Depends(get_db)
):
    """Get all files uploaded by a specific user."""
    service = DataFileService(session)
    files = service.get_user_files(user_id)
    return files


@router.get(
    "/public/files",
    response_model=list[FileMetadataResponse],
    summary="Get public files",
    description="Get all public files"
)
def get_public_files(
    dataset_id: Optional[int] = Query(None, description="Filter by dataset"),
    session: Session = Depends(get_db)
):
    """Get all public files, optionally filtered by dataset."""
    service = DataFileService(session)
    files = service.get_public_files(dataset_id)
    return files
