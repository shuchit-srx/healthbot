from unittest.mock import MagicMock, patch

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
    assert service.current_key_index == 1
    assert first_llm.invoke.call_count == 1
    assert second_llm.invoke.call_count == 1

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
        try:
            service.generate_with_gemini(
                "Explain diabetes."
            )
            assert False, (
                "Expected RuntimeError"
            )
        except RuntimeError as exc:
            assert (
                "all 3 API keys"
                in str(exc)
            )