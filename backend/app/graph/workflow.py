from langgraph.graph import END, START, StateGraph

from app.core.logging import get_logger
from app.graph.nodes import (
    generate_quiz_node,
    grade_answer_node,
    search_node,
    session_decision_node,
    summarize_information_node,
    validate_topic_node,
)
from app.graph.state import HealthBotState


logger = get_logger(__name__)


def route_after_validation(
    state: HealthBotState,
) -> str:
    """Route the workflow after topic validation."""

    if state.get("error"):
        return "end"

    if state.get("topic"):
        return "search"

    return "end"


def route_after_search(
    state: HealthBotState,
) -> str:
    """Route the workflow after medical information search."""

    if state.get("error"):
        return "end"

    if state.get("search_results"):
        return "summarize"

    return "end"


def route_after_summary(
    state: HealthBotState,
) -> str:
    """Route the workflow after summary generation."""

    if state.get("error"):
        return "end"

    if state.get("summary"):
        return "generate_quiz"

    return "end"


def route_after_quiz(
    state: HealthBotState,
) -> str:
    """Route the workflow after quiz generation."""

    if state.get("error"):
        return "end"

    if state.get("quiz_question"):
        return "grade_answer"

    return "end"


def route_after_grading(
    state: HealthBotState,
) -> str:
    """Route the workflow after answer grading."""

    if state.get("error"):
        return "end"

    if state.get("quiz_completed"):
        return "session_decision"

    return "end"


def route_after_session(
    state: HealthBotState,
) -> str:
    """Route the workflow based on the session decision."""

    if state.get("continue_session"):
        return "validate_topic"

    return "end"


def build_healthbot_workflow():
    """Build and compile the HealthBot LangGraph workflow."""

    graph = StateGraph(HealthBotState)

    # Register nodes
    graph.add_node(
        "validate_topic",
        validate_topic_node,
    )

    graph.add_node(
        "search",
        search_node,
    )

    graph.add_node(
        "summarize",
        summarize_information_node,
    )

    graph.add_node(
        "generate_quiz",
        generate_quiz_node,
    )

    graph.add_node(
        "grade_answer",
        grade_answer_node,
    )

    graph.add_node(
        "session_decision",
        session_decision_node,
    )

    # Entry point
    graph.add_edge(
        START,
        "validate_topic",
    )

    # Conditional routing
    graph.add_conditional_edges(
        "validate_topic",
        route_after_validation,
        {
            "search": "search",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "search",
        route_after_search,
        {
            "summarize": "summarize",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "summarize",
        route_after_summary,
        {
            "generate_quiz": "generate_quiz",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "generate_quiz",
        route_after_quiz,
        {
            "grade_answer": "grade_answer",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "grade_answer",
        route_after_grading,
        {
            "session_decision": "session_decision",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "session_decision",
        route_after_session,
        {
            "validate_topic": "validate_topic",
            "end": END,
        },
    )

    return graph.compile()


healthbot_workflow = build_healthbot_workflow()