from typing import Any

from langchain_tavily import TavilySearch

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.helpers import is_valid_text
from app.utils.retry import retry_operation


logger = get_logger(__name__)


class TavilyService:
    """Service responsible for retrieving medical information from Tavily."""

    def __init__(self):
        self.tool = TavilySearch(
            max_results=5,
            tavily_api_key=settings.tavily_api_key,
        )

    def search_medical_information(
        self,
        topic: str,
    ) -> list[dict[str, Any]]:
        """Search and validate medical information."""

        if not is_valid_text(topic):
            raise ValueError("Health topic cannot be empty.")

        def perform_search() -> list[dict[str, Any]]:
            logger.debug(
                "Searching Tavily for medical topic: %s",
                topic,
            )

            response = self.tool.invoke(
                {
                    "query": (
                        f"{topic} medical information "
                        "reputable sources"
                    )
                }
            )

            if not isinstance(response, dict):
                raise ValueError(
                    "Tavily returned an unexpected response format."
                )

            results = response.get("results", [])

            if not isinstance(results, list):
                raise ValueError(
                    "Tavily results are in an unexpected format."
                )

            valid_results = []

            for result in results:
                if not isinstance(result, dict):
                    continue

                content = result.get("content", "")

                if not is_valid_text(content):
                    continue

                valid_results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": content,
                        "score": result.get("score", 0),
                    }
                )

            if not valid_results:
                raise ValueError(
                    "Tavily returned no usable medical information."
                )

            logger.debug(
                "Tavily returned %d usable results.",
                len(valid_results),
            )

            return valid_results

        try:
            return retry_operation(
                perform_search,
                max_attempts=3,
                delay=2,
            )

        except Exception as exc:
            logger.exception(
                "Tavily request failed after retries."
            )
            raise RuntimeError(
                f"Tavily service failed: {exc}"
            ) from exc