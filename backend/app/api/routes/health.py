from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the current API health status."""

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }