from app.core.logging import get_logger
from app.core.prompts import (
    GRADING_PROMPT,
    QUIZ_PROMPT,
    SUMMARY_PROMPT,
)
from app.services.gemini import GeminiService
from app.services.response_parser import extract_grade
from app.services.tavily import TavilyService
from app.services.topic_validator import TopicValidator
from app.utils.helpers import format_prompt
from app.utils.state_helpers import create_error_state
from app.graph.state import HealthBotState


logger = get_logger(__name__)


gemini_service = GeminiService()
tavily_service = TavilyService()
topic_validator = TopicValidator()


def validate_topic_node(
    state: HealthBotState,
) -> HealthBotState:
    """Validate and normalize the user's health topic."""

    topic = state.get("topic", "")

    try:
        is_valid, normalized_topic = (
            topic_validator.validate_health_topic(topic)
        )

        if not is_valid:
            return create_error_state(
                "The provided topic is not recognized as a health topic."
            )

        return {
            **state,
            "topic": normalized_topic,
            "error": "",
        }

    except Exception as exc:
        logger.exception(
            "Topic validation node failed."
        )

        return create_error_state(
            f"Topic validation failed: {exc}"
        )


def search_node(
    state: HealthBotState,
) -> HealthBotState:
    """Retrieve medical information for the validated topic."""

    topic = state.get("topic", "")

    try:
        results = tavily_service.search_medical_information(
            topic
        )

        return {
            **state,
            "search_results": results,
            "error": "",
        }

    except Exception as exc:
        logger.exception(
            "Search node failed."
        )

        return create_error_state(
            f"Medical information search failed: {exc}"
        )


def summarize_information_node(
    state: HealthBotState,
) -> HealthBotState:
    """Generate a patient-friendly summary from search results."""

    topic = state.get("topic", "")
    search_results = state.get("search_results", [])

    if not search_results:
        return create_error_state(
            "No medical information is available for summarization."
        )

    try:
        prompt = format_prompt(
            SUMMARY_PROMPT,
            topic=topic,
            search_results=search_results,
        )

        summary = gemini_service.generate_with_gemini(
            prompt
        )

        return {
            **state,
            "summary": summary,
            "ready_for_quiz": True,
            "error": "",
        }

    except Exception as exc:
        logger.exception(
            "Summary generation node failed."
        )

        return create_error_state(
            f"Summary generation failed: {exc}"
        )


def generate_quiz_node(
    state: HealthBotState,
) -> HealthBotState:
    """Generate one comprehension question from the summary."""

    summary = state.get("summary", "")

    if not summary:
        return create_error_state(
            "Cannot generate a quiz without a summary."
        )

    try:
        prompt = format_prompt(
            QUIZ_PROMPT,
            summary=summary,
        )

        question = gemini_service.generate_with_gemini(
            prompt
        )

        return {
            **state,
            "quiz_question": question,
            "quiz_completed": False,
            "error": "",
        }

    except Exception as exc:
        logger.exception(
            "Quiz generation node failed."
        )

        return create_error_state(
            f"Quiz generation failed: {exc}"
        )


def grade_answer_node(
    state: HealthBotState,
) -> HealthBotState:
    """Grade the user's answer against the generated summary."""

    topic = state.get("topic", "")
    summary = state.get("summary", "")
    quiz_question = state.get("quiz_question", "")
    user_answer = state.get("user_answer", "")

    if not topic:
        return create_error_state(
            "Health topic is required for grading."
        )

    if not summary:
        return create_error_state(
            "Cannot grade an answer without a summary."
        )

    if not quiz_question:
        return create_error_state(
            "Cannot grade an answer without a quiz question."
        )

    if not user_answer:
        return create_error_state(
            "User answer cannot be empty."
        )

    try:
        prompt = format_prompt(
            GRADING_PROMPT,
            topic=topic,
            summary=summary,
            quiz_question=quiz_question,
            user_answer=user_answer,
        )

        feedback = gemini_service.generate_with_gemini(
            prompt
        )

        grade = extract_grade(feedback)

        if not grade:
            return create_error_state(
                "Unable to determine a valid quiz grade."
            )

        return {
            **state,
            "grade": grade,
            "feedback": feedback,
            "quiz_completed": True,
            "error": "",
        }

    except Exception as exc:
        logger.exception(
            "Answer grading node failed."
        )

        return create_error_state(
            f"Answer grading failed: {exc}"
        )


def session_decision_node(
    state: HealthBotState,
) -> HealthBotState:
    """Store the user's decision about continuing the session."""

    continue_session = state.get(
        "continue_session",
        False,
    )

    return {
        **state,
        "continue_session": continue_session,
    }