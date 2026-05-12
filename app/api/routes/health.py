from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["health"]
)


@router.get("/health")
def health_check() -> dict:
    """Basic liveness probe response."""
    return {
        "status": "ok",
        "service": "OpenDataInsight API"
    }

