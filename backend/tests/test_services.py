from unittest.mock import MagicMock, patch

import pytest

from app.services.gemini import GeminiService
from app.services.response_parser import (
    extract_grade,
    extract_section,
)
from app.services.tavily import TavilyService
from app.services.topic_validator import TopicValidator
from app.utils.retry import retry_operation


def test_gemini_rejects_empty_prompt():
    service = GeminiService()

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        service.generate_with_gemini("")


def test_tavily_rejects_empty_topic():
    service = TavilyService()

    with pytest.raises(
        ValueError,
        match="Health topic cannot be empty",
    ):
        service.search_medical_information("")


def test_topic_normalization():
    validator = TopicValidator()

    assert validator.normalize_topic(
        "  Type-2_Diabetes  "
    ) == "type 2 diabetes"


def test_exact_health_topic():
    validator = TopicValidator()

    assert validator.exact_health_match(
        "diabetes"
    ) is True

    assert validator.exact_health_match(
        "football"
    ) is False


def test_fuzzy_health_topic():
    validator = TopicValidator()

    matched_topic, score = (
        validator.fuzzy_health_match("diabtes")
    )

    assert matched_topic == "diabetes"
    assert score >= 85


def test_gemini_empty_response():
    service = GeminiService()

    mock_llm = MagicMock()

    mock_llm.invoke.return_value = MagicMock(
        content=""
    )

    service.api_keys = [
        "key_1"
    ]

    with patch.object(
        service,
        "llm",
        mock_llm,
    ):
        with pytest.raises(
            RuntimeError,
            match="Gemini service failed",
        ):
            service.generate_with_gemini(
                "Explain diabetes."
            )

def test_tavily_invalid_response():
    service = TavilyService()

    mock_tool = MagicMock()

    mock_tool.invoke.return_value = []

    with patch.object(
        service,
        "tool",
        mock_tool,
    ):
        with pytest.raises(
            RuntimeError,
            match="Tavily service failed",
        ):
            service.search_medical_information(
                "diabetes"
            )


def test_extract_grade():
    assert extract_grade(
        "Grade: A\n\nExplanation: Correct."
    ) == "A"

    assert extract_grade("Grade: B") == "B"
    assert extract_grade("Grade: C") == "C"
    assert extract_grade("Grade: D") == "D"
    assert extract_grade("Invalid response") == ""


def test_extract_section():
    response = """
Grade: A

Explanation:
The answer is correct.

Evidence:
Blood glucose regulation is discussed.

Source:
Medical source
"""

    assert extract_section(
        response,
        "Explanation",
    ) == "The answer is correct."

    assert extract_section(
        response,
        "Evidence",
    ) == "Blood glucose regulation is discussed."

    assert extract_section(
        response,
        "Source",
    ) == "Medical source"


def test_retry_success_after_failure():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1

        if attempts["count"] < 2:
            raise ValueError("Temporary failure")

        return "success"

    with patch(
        "app.utils.retry.time.sleep"
    ):
        result = retry_operation(
            operation,
            max_attempts=3,
            delay=0,
        )

    assert result == "success"
    assert attempts["count"] == 2


def test_retry_failure():
    def operation():
        raise ValueError("Permanent failure")

    with patch(
        "app.utils.retry.time.sleep"
    ):
        with pytest.raises(
            RuntimeError,
            match="Operation failed after 3 attempts",
        ):
            retry_operation(
                operation,
                max_attempts=3,
                delay=0,
            )