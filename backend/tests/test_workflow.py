from unittest.mock import patch

from app.graph.workflow import (
    route_after_grading,
    route_after_quiz,
    route_after_search,
    route_after_session,
    route_after_summary,
    route_after_validation,
)
from app.services.workflow import HealthBotWorkflowService
from app.utils.state_helpers import validate_state


def test_route_after_validation():
    assert route_after_validation(
        {"topic": "diabetes"}
    ) == "search"

    assert route_after_validation(
        {"error": "Invalid topic"}
    ) == "end"


def test_route_after_search():
    assert route_after_search(
        {
            "search_results": [
                {"content": "Medical information"}
            ]
        }
    ) == "summarize"

    assert route_after_search(
        {"error": "Search failed"}
    ) == "end"


def test_route_after_summary():
    assert route_after_summary(
        {"summary": "Diabetes information"}
    ) == "generate_quiz"

    assert route_after_summary(
        {"error": "Summary failed"}
    ) == "end"


def test_route_after_quiz():
    assert route_after_quiz(
        {"quiz_question": "What is diabetes?"}
    ) == "grade_answer"

    assert route_after_quiz(
        {"error": "Quiz failed"}
    ) == "end"


def test_route_after_grading():
    assert route_after_grading(
        {"quiz_completed": True}
    ) == "session_decision"

    assert route_after_grading(
        {"error": "Grading failed"}
    ) == "end"


def test_route_after_session():
    assert route_after_session(
        {"continue_session": True}
    ) == "validate_topic"

    assert route_after_session(
        {"continue_session": False}
    ) == "end"


def test_state_validation():
    assert validate_state(
        {
            "topic": "diabetes",
            "summary": "Medical information",
        }
    ) is True

    assert validate_state(
        {
            "topic": 123,
        }
    ) is False


def test_workflow_service(mock_tavily_results):
    service = HealthBotWorkflowService()

    initial_state = {
        "topic": "diabetes",
        "user_answer": "It affects blood glucose.",
        "continue_session": False,
    }

    with patch(
        "app.graph.nodes.topic_validator.validate_health_topic",
        return_value=(True, "diabetes"),
    ), patch(
        "app.graph.nodes.tavily_service.search_medical_information",
        return_value=mock_tavily_results,
    ), patch(
        "app.graph.nodes.gemini_service.generate_with_gemini",
        side_effect=[
            "Diabetes is a condition affecting blood glucose.",
            "What does diabetes affect?",
            "Grade: A\n\nExplanation: Correct.",
        ],
    ):
        result = service.run(initial_state)

    assert result["topic"] == "diabetes"
    assert result["search_results"]
    assert result["summary"]
    assert result["quiz_question"]
    assert result["grade"] == "A"
    assert result["quiz_completed"] is True