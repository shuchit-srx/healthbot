from fastapi import FastAPI

from app.core.config import settings
from app.core.error_handlers import (
    generic_exception_handler,
    healthbot_exception_handler,
)
from app.core.exceptions import HealthBotError
from app.core.logging import get_logger, setup_logging


setup_logging(settings.debug)

logger = get_logger(__name__)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered patient education assistant.",
)


app.add_exception_handler(
    HealthBotError,
    healthbot_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the current API health status."""

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API information."""

    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }