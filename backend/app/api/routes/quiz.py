from fastapi import APIRouter

from app.core.prompts import QUIZ_PROMPT
from app.models.responses import QuizResponse
from app.services.gemini import GeminiService
from app.utils.helpers import format_prompt


router = APIRouter(
    prefix="/api/quiz",
    tags=["Quiz"],
)


gemini_service = GeminiService()


@router.post(
    "/generate",
    response_model=QuizResponse,
)
def generate_quiz(
    summary: str,
) -> QuizResponse:
    """Generate a comprehension question from a summary."""

    if not summary.strip():
        raise ValueError(
            "Summary cannot be empty."
        )

    prompt = format_prompt(
        QUIZ_PROMPT,
        summary=summary,
    )

    question = gemini_service.generate_with_gemini(
        prompt
    )

    return QuizResponse(
        question=question,
    )