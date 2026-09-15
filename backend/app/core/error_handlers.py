from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import HealthBotError
from app.core.logging import get_logger


logger = get_logger(__name__)


async def healthbot_exception_handler(
    request: Request,
    exc: HealthBotError,
) -> JSONResponse:
    """Handle known HealthBot application errors."""

    logger.error(
        "HealthBot error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "detail": str(exc),
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected application errors."""

    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred.",
        },
    )