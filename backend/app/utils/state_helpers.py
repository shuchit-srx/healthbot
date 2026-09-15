from app.graph.state import HealthBotState


def create_error_state(message: str) -> HealthBotState:
    """Create a consistent error state for the HealthBot workflow."""

    return {"error": message}


def reset_state() -> HealthBotState:
    """Reset the workflow state for a new session."""

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