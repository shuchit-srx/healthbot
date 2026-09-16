from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.education import router as education_router
from app.api.routes.grading import router as grading_router
from app.api.routes.quiz import router as quiz_router
from app.api.routes.session import router as session_router
from app.api.routes.topic import router as topic_router
from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


app = FastAPI(
    title="HealthBot API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


@app.middleware("http")
async def security_headers(
    request: Request,
    call_next,
):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled application error."
        )

        response = JSONResponse(
            status_code=500,
            content={
                "detail": (
                    "An internal error occurred. "
                    "Please try again."
                )
            },
        )

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    return response


@app.get("/")
def root():
    return {
        "service": "HealthBot",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HealthBot",
        "version": "1.0.0",
    }


app.include_router(
    topic_router,
)

app.include_router(
    education_router,
)

app.include_router(
    quiz_router,
)

app.include_router(
    grading_router,
)

app.include_router(
    session_router,
)