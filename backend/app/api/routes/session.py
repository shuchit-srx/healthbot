from fastapi import APIRouter

from app.models.requests import SessionDecisionRequest
from app.models.responses import HealthBotStateResponse


router = APIRouter(
    prefix="/api/session",
    tags=["Session"],
)


@router.post(
    "/decision",
    response_model=HealthBotStateResponse,
)
def session_decision(
    request: SessionDecisionRequest,
) -> HealthBotStateResponse:
    """Return the user's session decision."""

    return HealthBotStateResponse(
        data={
            "continue_session": request.continue_session,
        }
    )