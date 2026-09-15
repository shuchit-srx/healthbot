from fastapi import APIRouter

from app.core.prompts import GRADING_PROMPT
from app.models.requests import QuizAnswerRequest
from app.models.responses import GradeResponse
from app.services.gemini import GeminiService
from app.services.response_parser import extract_grade
from app.utils.helpers import format_prompt


router = APIRouter(
    prefix="/api/quiz",
    tags=["Quiz"],
)


gemini_service = GeminiService()


@router.post(
    "/grade",
    response_model=GradeResponse,
)
def grade_answer(
    request: QuizAnswerRequest,
    topic: str,
    summary: str,
    quiz_question: str,
) -> GradeResponse:
    """Grade a user's answer."""

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    if not summary.strip():
        raise ValueError(
            "Summary cannot be empty."
        )

    if not quiz_question.strip():
        raise ValueError(
            "Quiz question cannot be empty."
        )

    prompt = format_prompt(
        GRADING_PROMPT,
        topic=topic,
        summary=summary,
        quiz_question=quiz_question,
        user_answer=request.user_answer,
    )

    feedback = gemini_service.generate_with_gemini(
        prompt
    )

    grade = extract_grade(feedback)

    if not grade:
        raise ValueError(
            "Unable to determine a valid quiz grade."
        )

    return GradeResponse(
        grade=grade,
        feedback=feedback,
    )