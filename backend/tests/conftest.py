import pytest


@pytest.fixture
def mock_gemini_response():
    return "Gemini test response."


@pytest.fixture
def mock_tavily_results():
    return [
        {
            "title": "Diabetes Information",
            "url": "https://example.com/diabetes",
            "content": "Diabetes affects blood glucose regulation.",
            "score": 0.95,
        }
    ]