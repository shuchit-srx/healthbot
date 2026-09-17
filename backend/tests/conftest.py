import os

import pytest


# Provide non-secret placeholder credentials so application services
# can be imported during CI test collection.
os.environ.setdefault(
    "GEMINI_API_KEY",
    "ci-test-gemini-key",
)

os.environ.setdefault(
    "TAVILY_API_KEY",
    "ci-test-tavily-key",
)


def pytest_collection_modifyitems(config, items):
    skip_integration = pytest.mark.skip(
        reason="Integration tests require external API credentials."
    )

    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def mock_tavily_results():
    return [
        {
            "title": "Diabetes Information",
            "url": "https://example.com/diabetes",
            "content": (
                "Diabetes affects blood glucose regulation."
            ),
            "score": 0.95,
        }
    ]


@pytest.fixture
def mock_summary():
    return (
        "Diabetes is a condition that affects "
        "blood glucose regulation."
    )


@pytest.fixture
def mock_quiz_question():
    return "What does diabetes affect?"


@pytest.fixture
def mock_grade_feedback():
    return (
        "Grade: A\n\n"
        "Explanation: The answer is correct."
    )


@pytest.fixture
def valid_workflow_state(
    mock_summary,
    mock_quiz_question,
):
    return {
        "topic": "diabetes",
        "search_results": [
            {
                "title": "Diabetes Information",
                "url": "https://example.com/diabetes",
                "content": (
                    "Diabetes affects blood glucose regulation."
                ),
                "score": 0.95,
            }
        ],
        "summary": mock_summary,
        "quiz_question": mock_quiz_question,
        "user_answer": "Blood glucose.",
        "grade": "",
        "feedback": "",
        "ready_for_quiz": True,
        "quiz_completed": False,
        "continue_session": False,
        "error": "",
    }