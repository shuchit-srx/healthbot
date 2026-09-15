from unittest.mock import patch

from app.services.workflow import HealthBotWorkflowService


def test_complete_healthbot_workflow(
    mock_tavily_results,
):
    service = HealthBotWorkflowService()

    initial_state = {
        "topic": "diabetes",
        "user_answer": "Diabetes affects blood glucose.",
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
            "Diabetes is a condition that affects blood glucose.",
            "What does diabetes affect?",
            "Grade: A\n\nExplanation: The answer is correct.",
        ],
    ):
        result = service.run(initial_state)

    assert result["error"] == ""
    assert result["topic"] == "diabetes"
    assert len(result["search_results"]) == 1
    assert result["summary"]
    assert result["ready_for_quiz"] is True
    assert result["quiz_question"]
    assert result["grade"] == "A"
    assert result["feedback"]
    assert result["quiz_completed"] is True
    assert result["continue_session"] is False