from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.education import router as education_router
from app.api.routes.grading import router as grading_router
from app.api.routes.health import router as health_router
from app.api.routes.quiz import router as quiz_router
from app.api.routes.session import router as session_router
from app.api.routes.topic import router as topic_router
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(topic_router)
app.include_router(education_router)
app.include_router(quiz_router)
app.include_router(grading_router)
app.include_router(session_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API information."""

    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }