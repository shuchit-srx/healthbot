from unittest.mock import MagicMock, patch

from app.services.gemini import GeminiService
from app.services.tavily import TavilyService


def test_gemini_retries_failed_request():
    service = GeminiService()

    mock_llm = MagicMock()

    mock_llm.invoke.side_effect = [
        RuntimeError("Temporary failure"),
        RuntimeError("Temporary failure"),
        MagicMock(
            content="Successful response"
        ),
    ]

    with patch.object(
        service,
        "llm",
        mock_llm,
    ), patch(
        "app.utils.retry.time.sleep"
    ):
        result = service.generate_with_gemini(
            "Explain diabetes."
        )

    assert result == "Successful response"
    assert mock_llm.invoke.call_count == 3


def test_tavily_retries_failed_request():
    service = TavilyService()

    mock_tool = MagicMock()

    mock_tool.invoke.side_effect = [
        RuntimeError("Temporary failure"),
        RuntimeError("Temporary failure"),
        {
            "results": [
                {
                    "title": "Diabetes",
                    "url": "https://example.com",
                    "content": "Diabetes information.",
                    "score": 0.9,
                }
            ]
        },
    ]

    with patch.object(
        service,
        "tool",
        mock_tool,
    ), patch(
        "app.utils.retry.time.sleep"
    ):
        result = service.search_medical_information(
            "diabetes"
        )

    assert len(result) == 1
    assert mock_tool.invoke.call_count == 3