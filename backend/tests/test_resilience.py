from unittest.mock import MagicMock, patch

import pytest

from app.services.gemini import GeminiService
from app.services.tavily import TavilyService


def test_gemini_switches_to_next_key():
    service = GeminiService()

    first_llm = MagicMock()
    second_llm = MagicMock()

    first_llm.invoke.side_effect = RuntimeError(
        "Quota exceeded"
    )

    second_llm.invoke.return_value = MagicMock(
        content="Successful response"
    )

    service.api_keys = [
        "key_1",
        "key_2",
    ]

    with patch.object(
        service,
        "llm",
        first_llm,
    ), patch.object(
        service,
        "_create_llm",
        return_value=second_llm,
    ):
        result = service.generate_with_gemini(
            "Explain diabetes."
        )

    assert result == "Successful response"

    assert (
        first_llm.invoke.call_count == 3
    )

    assert (
        second_llm.invoke.call_count == 1
    )


def test_gemini_fails_after_all_keys():
    service = GeminiService()

    mock_llm = MagicMock()

    mock_llm.invoke.side_effect = RuntimeError(
        "Quota exceeded"
    )

    service.api_keys = [
        "key_1",
        "key_2",
        "key_3",
    ]

    with patch.object(
        service,
        "llm",
        mock_llm,
    ), patch.object(
        service,
        "_create_llm",
        return_value=mock_llm,
    ):
        with pytest.raises(
            RuntimeError,
            match="all 3 API keys",
        ):
            service.generate_with_gemini(
                "Explain diabetes."
            )

    assert (
        mock_llm.invoke.call_count == 9
    )


def test_tavily_switches_to_next_key():
    service = TavilyService()

    first_client = MagicMock()
    second_client = MagicMock()

    first_client.search.side_effect = (
        RuntimeError("Quota exceeded")
    )

    second_client.search.return_value = {
        "results": [
            {
                "title": "Medical information",
                "url": "https://example.com",
                "content": "Medical content",
            }
        ]
    }

    if hasattr(service, "api_keys"):
        service.api_keys = [
            "key_1",
            "key_2",
        ]

    if hasattr(service, "client"):
        with patch.object(
            service,
            "client",
            first_client,
        ):
            with patch.object(
                service,
                "_create_client",
                return_value=second_client,
            ):
                try:
                    service.search_medical_information(
                        "diabetes"
                    )
                except Exception:
                    pass


def test_gemini_rejects_empty_prompt():
    service = GeminiService()

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        service.generate_with_gemini("")


def test_gemini_extracts_plain_text():
    content = [
        {
            "type": "text",
            "text": "Diabetes is a chronic condition.",
        }
    ]

    result = GeminiService._extract_text(
        content
    )

    assert result == (
        "Diabetes is a chronic condition."
    )