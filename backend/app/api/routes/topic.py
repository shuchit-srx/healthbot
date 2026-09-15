from fastapi import APIRouter

from app.models.requests import HealthTopicRequest
from app.models.responses import HealthTopicResponse
from app.services.topic_validator import TopicValidator


router = APIRouter(
    prefix="/api/topics",
    tags=["Topics"],
)


topic_validator = TopicValidator()


@router.post(
    "/validate",
    response_model=HealthTopicResponse,
)
def validate_topic(
    request: HealthTopicRequest,
) -> HealthTopicResponse:
    """Validate and normalize a health topic."""

    is_valid, normalized_topic = (
        topic_validator.validate_health_topic(
            request.topic
        )
    )

    if not is_valid:
        return HealthTopicResponse(
            valid=False,
            error="The provided topic is not a valid health topic.",
        )

    return HealthTopicResponse(
        valid=True,
        topic=normalized_topic,
    )