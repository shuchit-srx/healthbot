from typing import Any, TypedDict


class HealthBotState(TypedDict, total=False):
    """Shared state passed between HealthBot workflow nodes."""

    topic: str
    search_results: list[dict[str, Any]]
    summary: str
    quiz_question: str
    user_answer: str
    grade: str
    feedback: str
    ready_for_quiz: bool
    quiz_completed: bool
    continue_session: bool
    error: str