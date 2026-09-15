import pytest

from app.services.gemini import GeminiService
from app.services.tavily import TavilyService


@pytest.mark.integration
def test_gemini_api():
    try:
        gemini_service = GeminiService()

        response = gemini_service.llm.invoke(
            "Reply with: Gemini API working"
        )

        assert response.content

    except Exception as e:
        pytest.fail(f"Gemini API failed: {e}")


@pytest.mark.integration
def test_tavily_api():
    try:
        tavily_service = TavilyService()

        response = tavily_service.tool.invoke(
            {"query": "diabetes medical information"}
        )

        assert response.get("results") is not None

    except Exception as e:
        pytest.fail(f"Tavily API failed: {e}")