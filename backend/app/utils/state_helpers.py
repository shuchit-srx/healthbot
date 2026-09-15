from app.graph.state import HealthBotState


def create_error_state(
    message: str,
) -> HealthBotState:
    """Create a consistent error state."""

    return {
        "error": message,
    }


def reset_state() -> HealthBotState:
    """Reset the HealthBot workflow state."""

    return {
        "topic": "",
        "search_results": [],
        "summary": "",
        "quiz_question": "",
        "user_answer": "",
        "grade": "",
        "feedback": "",
        "ready_for_quiz": False,
        "quiz_completed": False,
        "continue_session": False,
        "error": "",
    }


def validate_state(
    state: HealthBotState,
) -> bool:
    """Validate the basic structure of workflow state."""

    if not isinstance(state, dict):
        return False

    topic = state.get("topic")

    if topic is not None and not isinstance(topic, str):
        return False

    search_results = state.get("search_results")

    if search_results is not None and not isinstance(
        search_results,
        list,
    ):
        return False

    summary = state.get("summary")

    if summary is not None and not isinstance(summary, str):
        return False

    quiz_question = state.get("quiz_question")

    if quiz_question is not None and not isinstance(
        quiz_question,
        str,
    ):
        return False

    user_answer = state.get("user_answer")

    if user_answer is not None and not isinstance(
        user_answer,
        str,
    ):
        return False

    grade = state.get("grade")

    if grade is not None and not isinstance(grade, str):
        return False

    feedback = state.get("feedback")

    if feedback is not None and not isinstance(
        feedback,
        str,
    ):
        return False

    return True