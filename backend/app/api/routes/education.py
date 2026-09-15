from fastapi import APIRouter

from app.models.requests import HealthTopicRequest
from app.models.responses import SummaryResponse
from app.services.tavily import TavilyService
from app.services.gemini import GeminiService
from app.core.prompts import SUMMARY_PROMPT
from app.utils.helpers import format_prompt


router = APIRouter(
    prefix="/api/education",
    tags=["Education"],
)


tavily_service = TavilyService()
gemini_service = GeminiService()


@router.post(
    "/summary",
    response_model=SummaryResponse,
)
def generate_summary(
    request: HealthTopicRequest,
) -> SummaryResponse:
    """Search medical information and generate a summary."""

    results = tavily_service.search_medical_information(
        request.topic
    )

    prompt = format_prompt(
        SUMMARY_PROMPT,
        topic=request.topic,
        search_results=results,
    )

    summary = gemini_service.generate_with_gemini(
        prompt
    )

    return SummaryResponse(
        topic=request.topic,
        summary=summary,
        sources=results,
    )