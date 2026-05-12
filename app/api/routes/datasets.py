from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.dataset_service import DatasetService


# Request/Response models
class DatasetCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: bool = True


class DatasetResponse(BaseModel):
    dataset_id: int
    owner_id: int
    name: str
    description: Optional[str]
    visibility: bool
    is_labeled: bool
    created_at: str
    updated_at: str


# Create router
router = APIRouter(
    prefix="/api/datasets",
    tags=["datasets"]
)


# Dependency to get database session (placeholder - replace with actual DB dependency)
def get_db():
    # This should be replaced with actual database session logic
    pass


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dataset",
    description="Create a new dataset"
)
def create_dataset(
    request: DatasetCreateRequest,
    user_id: int = Query(..., description="Owner user ID"),
    session: Session = Depends(get_db)
):
    """Create a new dataset."""
    try:
        service = DatasetService(session)
        dataset = service.create_dataset(
            owner_id=user_id,
            name=request.name,
            description=request.description,
            visibility=request.visibility
        )
        return dataset
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Get dataset",
    description="Retrieve a dataset by ID"
)
def get_dataset(
    dataset_id: int,
    session: Session = Depends(get_db)
):
    """Get a dataset by ID."""
    service = DatasetService(session)
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return dataset


@router.get(
    "",
    response_model=List[DatasetResponse],
    summary="List datasets",
    description="List all datasets, optionally filtered"
)
def list_datasets(
    user_id: Optional[int] = Query(None, description="Filter by owner user ID"),
    public_only: bool = Query(False, description="Show only public datasets"),
    session: Session = Depends(get_db)
):
    """List datasets."""
    service = DatasetService(session)
    
    if user_id:
        datasets = service.get_user_datasets(user_id)
    elif public_only:
        datasets = service.get_public_datasets()
    else:
        datasets = service.get_public_datasets()
    
    return datasets


@router.put(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Update dataset",
    description="Update dataset metadata"
)
def update_dataset(
    dataset_id: int,
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    visibility: Optional[bool] = Query(None),
    session: Session = Depends(get_db)
):
    """Update a dataset."""
    try:
        service = DatasetService(session)
        updates = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if visibility is not None:
            updates["visibility"] = visibility
        
        dataset = service.update_dataset(dataset_id, **updates)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        return dataset
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete dataset",
    description="Delete a dataset"
)
def delete_dataset(
    dataset_id: int,
    session: Session = Depends(get_db)
):
    """Delete a dataset."""
    service = DatasetService(session)
    success = service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
