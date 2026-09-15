from langgraph.graph import StateGraph, START, END
from app.graph.nodes import route_quiz

from app.graph.nodes import (
    display_feedback,
    display_summary,
    generate_quiz,
    get_quiz_answer,
    get_topic,
    grade_answer,
    reset_state_node,
    search_node,
    session_decision,
    summarize_information,
)
from app.graph.state import HealthBotState


healthbot_graph = StateGraph(HealthBotState)


healthbot_graph.add_node("get_topic", get_topic)
healthbot_graph.add_node("search", search_node)
healthbot_graph.add_node("summarize", summarize_information)
healthbot_graph.add_node("display_summary", display_summary)
healthbot_graph.add_node("generate_quiz", generate_quiz)
healthbot_graph.add_node("get_quiz_answer", get_quiz_answer)
healthbot_graph.add_node("grade_answer", grade_answer)
healthbot_graph.add_node("display_feedback", display_feedback)
healthbot_graph.add_node("session_decision", session_decision)
healthbot_graph.add_node("reset_state", reset_state_node)

healthbot_graph.add_edge(START, "get_topic")
healthbot_graph.add_edge("get_topic", "search")
healthbot_graph.add_edge("search", "summarize")
healthbot_graph.add_edge("summarize", "display_summary")
healthbot_graph.add_edge("generate_quiz", "get_quiz_answer")
healthbot_graph.add_edge("get_quiz_answer", "grade_answer")
healthbot_graph.add_edge("grade_answer", "display_feedback")
healthbot_graph.add_edge("display_feedback", "session_decision")

healthbot_graph.add_conditional_edges(
    "display_summary",
    route_quiz,
    {
        "generate_quiz": "generate_quiz",
        "session_decision": "session_decision",
    },
)

def route_session(state: HealthBotState) -> str:
    """Route the workflow based on the user's session decision."""

    if state.get("continue_session", False):
        return "reset_state"

    return END

healthbot_graph.add_conditional_edges(
    "session_decision",
    route_session,
    {
        "reset_state": "reset_state",
        END: END,
    },
)

healthbot_graph.add_edge(
    "reset_state",
    "get_topic",
)

healthbot_app = healthbot_graph.compile()