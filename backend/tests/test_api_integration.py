from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_topic_to_summary_flow(
    mock_tavily_results,
):
    with patch(
        "app.api.routes.topic.topic_validator.validate_health_topic",
        return_value=(True, "diabetes"),
    ):
        topic_response = client.post(
            "/api/topics/validate",
            json={
                "topic": "diabetes",
            },
        )

    assert topic_response.status_code == 200

    topic_data = topic_response.json()

    assert topic_data["valid"] is True

    with patch(
        "app.api.routes.education.tavily_service.search_medical_information",
        return_value=mock_tavily_results,
    ), patch(
        "app.api.routes.education.gemini_service.generate_with_gemini",
        return_value="Diabetes affects blood glucose.",
    ):
        summary_response = client.post(
            "/api/education/summary",
            json={
                "topic": topic_data["topic"],
            },
        )

    assert summary_response.status_code == 200

    summary_data = summary_response.json()

    assert summary_data["summary"]
    assert summary_data["sources"]


def test_quiz_to_grade_flow():
    summary = (
        "Diabetes affects blood glucose regulation."
    )

    with patch(
        "app.api.routes.quiz.gemini_service.generate_with_gemini",
        return_value="What does diabetes affect?",
    ):
        quiz_response = client.post(
            "/api/quiz/generate",
            params={
                "summary": summary,
            },
        )

    assert quiz_response.status_code == 200

    question = quiz_response.json()["question"]

    with patch(
        "app.api.routes.grading.gemini_service.generate_with_gemini",
        return_value=(
            "Grade: A\n\n"
            "Explanation: Correct."
        ),
    ):
        grade_response = client.post(
            "/api/quiz/grade",
            params={
                "topic": "diabetes",
                "summary": summary,
                "quiz_question": question,
            },
            json={
                "user_answer": "Blood glucose.",
            },
        )

    assert grade_response.status_code == 200

    grade_data = grade_response.json()

    assert grade_data["grade"] == "A"
    assert grade_data["feedback"]