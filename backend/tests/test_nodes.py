from unittest.mock import MagicMock, patch

from app.graph.nodes import (
    generate_quiz_node,
    grade_answer_node,
    search_node,
    session_decision_node,
    summarize_information_node,
    validate_topic_node,
)


def test_validate_topic_node():
    state = {
        "topic": "diabetes",
    }

    with patch(
        "app.graph.nodes.topic_validator.validate_health_topic",
        return_value=(True, "diabetes"),
    ):
        result = validate_topic_node(state)

    assert result["topic"] == "diabetes"
    assert result["error"] == ""


def test_validate_topic_node_invalid():
    state = {
        "topic": "football",
    }

    with patch(
        "app.graph.nodes.topic_validator.validate_health_topic",
        return_value=(False, ""),
    ):
        result = validate_topic_node(state)

    assert "error" in result


def test_search_node(mock_tavily_results):
    state = {
        "topic": "diabetes",
    }

    with patch(
        "app.graph.nodes.tavily_service.search_medical_information",
        return_value=mock_tavily_results,
    ):
        result = search_node(state)

    assert result["search_results"]
    assert result["error"] == ""


def test_search_node_failure():
    state = {
        "topic": "diabetes",
    }

    with patch(
        "app.graph.nodes.tavily_service.search_medical_information",
        side_effect=RuntimeError("Search failed"),
    ):
        result = search_node(state)

    assert "Search failed" in result["error"]


def test_summary_node(mock_tavily_results):
    state = {
        "topic": "diabetes",
        "search_results": mock_tavily_results,
    }

    with patch(
        "app.graph.nodes.gemini_service.generate_with_gemini",
        return_value="Diabetes affects blood glucose.",
    ):
        result = summarize_information_node(state)

    assert result["summary"]
    assert result["ready_for_quiz"] is True
    assert result["error"] == ""


def test_summary_node_without_results():
    state = {
        "topic": "diabetes",
        "search_results": [],
    }

    result = summarize_information_node(state)

    assert "error" in result


def test_quiz_node():
    state = {
        "summary": "Diabetes affects blood glucose.",
    }

    with patch(
        "app.graph.nodes.gemini_service.generate_with_gemini",
        return_value="What does diabetes affect?",
    ):
        result = generate_quiz_node(state)

    assert result["quiz_question"]
    assert result["quiz_completed"] is False


def test_quiz_node_without_summary():
    result = generate_quiz_node(
        {
            "summary": "",
        }
    )

    assert "error" in result


def test_grade_answer_node():
    state = {
        "topic": "diabetes",
        "summary": "Diabetes affects blood glucose.",
        "quiz_question": "What does diabetes affect?",
        "user_answer": "Blood glucose.",
    }

    with patch(
        "app.graph.nodes.gemini_service.generate_with_gemini",
        return_value=(
            "Grade: A\n\nExplanation: Correct."
        ),
    ):
        result = grade_answer_node(state)

    assert result["grade"] == "A"
    assert result["quiz_completed"] is True
    assert result["feedback"]


def test_grade_answer_without_question():
    result = grade_answer_node(
        {
            "topic": "diabetes",
            "summary": "Diabetes affects blood glucose.",
            "quiz_question": "",
            "user_answer": "Blood glucose.",
        }
    )

    assert "error" in result


def test_grade_answer_without_user_answer():
    result = grade_answer_node(
        {
            "topic": "diabetes",
            "summary": "Diabetes affects blood glucose.",
            "quiz_question": "What does diabetes affect?",
            "user_answer": "",
        }
    )

    assert "error" in result


def test_session_decision():
    result = session_decision_node(
        {
            "continue_session": True,
        }
    )

    assert result["continue_session"] is True