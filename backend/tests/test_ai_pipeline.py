from unittest.mock import MagicMock, patch

from app.services.gemini import GeminiService
from app.services.tavily import TavilyService
from app.services.topic_validator import TopicValidator


def test_topic_validation_pipeline():
    validator = TopicValidator()

    is_valid, topic = validator.validate_health_topic(
        "diabetes"
    )

    assert is_valid is True
    assert topic == "diabetes"


def test_tavily_service_pipeline(mock_tavily_results):
    service = TavilyService()

    mock_tool = MagicMock()
    mock_tool.invoke.return_value = {
        "results": mock_tavily_results
    }

    with patch.object(
        service,
        "tool",
        mock_tool,
    ):
        results = service.search_medical_information(
            "diabetes"
        )

    assert len(results) == 1
    assert results[0]["title"] == "Diabetes Information"


def test_gemini_service_pipeline():
    service = GeminiService()

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="Diabetes affects blood glucose regulation."
    )

    with patch.object(
        service,
        "llm",
        mock_llm,
    ):
        result = service.generate_with_gemini(
            "Explain diabetes."
        )

    assert result == (
        "Diabetes affects blood glucose regulation."
    )