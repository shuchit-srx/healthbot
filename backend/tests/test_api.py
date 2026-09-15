from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "HealthBot"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "HealthBot"
    assert data["version"] == "1.0.0"


def test_not_found_endpoint():
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_topic_validation():
    with patch(
        "app.api.routes.topic.topic_validator.validate_health_topic",
        return_value=(True, "diabetes"),
    ):
        response = client.post(
            "/api/topics/validate",
            json={
                "topic": "diabetes",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["valid"] is True
    assert data["topic"] == "diabetes"


def test_topic_validation_invalid():
    with patch(
        "app.api.routes.topic.topic_validator.validate_health_topic",
        return_value=(False, ""),
    ):
        response = client.post(
            "/api/topics/validate",
            json={
                "topic": "football",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["valid"] is False


def test_summary_endpoint(mock_tavily_results):
    with patch(
        "app.api.routes.education.tavily_service.search_medical_information",
        return_value=mock_tavily_results,
    ), patch(
        "app.api.routes.education.gemini_service.generate_with_gemini",
        return_value="Diabetes affects blood glucose regulation.",
    ):
        response = client.post(
            "/api/education/summary",
            json={
                "topic": "diabetes",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["topic"] == "diabetes"
    assert data["summary"]
    assert len(data["sources"]) == 1


def test_quiz_endpoint():
    with patch(
        "app.api.routes.quiz.gemini_service.generate_with_gemini",
        return_value="What does diabetes affect?",
    ):
        response = client.post(
            "/api/quiz/generate",
            params={
                "summary": "Diabetes affects blood glucose."
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]


def test_grade_endpoint():
    with patch(
        "app.api.routes.grading.gemini_service.generate_with_gemini",
        return_value="Grade: A\n\nExplanation: Correct.",
    ):
        response = client.post(
            "/api/quiz/grade",
            params={
                "topic": "diabetes",
                "summary": "Diabetes affects blood glucose.",
                "quiz_question": "What does diabetes affect?",
            },
            json={
                "user_answer": "Blood glucose.",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["grade"] == "A"
    assert data["feedback"]


def test_session_endpoint():
    response = client.post(
        "/api/session/decision",
        json={
            "continue_session": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["data"]["continue_session"] is True


def test_topic_validation_empty():
    response = client.post(
        "/api/topics/validate",
        json={
            "topic": "",
        },
    )

    assert response.status_code == 422


def test_topic_validation_too_long():
    response = client.post(
        "/api/topics/validate",
        json={
            "topic": "a" * 201,
        },
    )

    assert response.status_code == 422


def test_quiz_answer_empty():
    response = client.post(
        "/api/quiz/grade",
        params={
            "topic": "diabetes",
            "summary": "Diabetes affects blood glucose.",
            "quiz_question": "What does diabetes affect?",
        },
        json={
            "user_answer": "",
        },
    )

    assert response.status_code == 422


def test_quiz_answer_too_long():
    response = client.post(
        "/api/quiz/grade",
        params={
            "topic": "diabetes",
            "summary": "Diabetes affects blood glucose.",
            "quiz_question": "What does diabetes affect?",
        },
        json={
            "user_answer": "a" * 2001,
        },
    )

    assert response.status_code == 422


def test_invalid_session_payload():
    response = client.post(
        "/api/session/decision",
        json={
            "continue_session": "invalid",
        },
    )

    assert response.status_code == 422