from fastapi import APIRouter

from app.core.prompts import GRADING_PROMPT
from app.models.requests import QuizAnswerRequest
from app.models.responses import GradeResponse
from app.services.gemini import GeminiService
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
def grade_quiz(
    topic: str,
    summary: str,
    quiz_question: str,
    request: QuizAnswerRequest,
) -> GradeResponse:
    prompt = format_prompt(
        GRADING_PROMPT,
        topic=topic,
        summary=summary,
        quiz_question=quiz_question,
        user_answer=request.user_answer,
    )

    result = gemini_service.generate_with_gemini(
        prompt
    )

    lines = result.splitlines()

    grade = "Ungraded"
    feedback = result

    for index, line in enumerate(lines):
        stripped = line.strip()

        if stripped.lower().startswith("grade:"):
            grade = stripped.split(
                ":",
                1,
            )[1].strip()

        if stripped.lower().startswith(
            "explanation:"
        ):
            feedback = stripped.split(
                ":",
                1,
            )[1].strip()

            remaining = lines[index + 1:]

            if remaining:
                feedback = (
                    feedback
                    + "\n"
                    + "\n".join(
                        remaining
                    ).strip()
                )

            break

    return GradeResponse(
        grade=grade,
        feedback=feedback.strip(),
    )