from fastapi import APIRouter

from app.models.requests import SessionDecisionRequest
from app.models.responses import HealthBotStateResponse


router = APIRouter(
    prefix="/api/session",
    tags=["Session"],
)


@router.post(
    "/decision",
)
def session_decision(
    request: SessionDecisionRequest,
) -> dict:
    """
    Store the user's decision about continuing
    the HealthBot session.
    """

    state = HealthBotStateResponse(
        continue_session=request.continue_session,
    )

    return {
        "data": state.model_dump(),
    }