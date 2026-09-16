from itertools import cycle

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.retry import retry_operation


logger = get_logger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini."""

    def __init__(self) -> None:
        if not settings.gemini_api_keys:
            raise ValueError(
                "No Gemini API keys configured."
            )

        self._api_keys = cycle(
            settings.gemini_api_keys
        )

        self.llm = self._create_llm()

    def _create_llm(self):
        """Create a Gemini client using the next API key."""

        api_key = next(self._api_keys)

        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=api_key,
        )

    @staticmethod
    def _extract_text(content) -> str:
        """
        Convert Gemini/LangChain response content
        into plain text.
        """

        # Normal string response
        if isinstance(content, str):
            return content.strip()

        # Structured response
        if isinstance(content, list):
            text_parts = []

            for item in content:

                # Example:
                # {
                #     "type": "text",
                #     "text": "..."
                # }
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text = item.get(
                            "text",
                            "",
                        )

                        if isinstance(text, str):
                            text_parts.append(
                                text
                            )

                # String item inside list
                elif isinstance(item, str):
                    text_parts.append(item)

            return "\n".join(
                part.strip()
                for part in text_parts
                if part.strip()
            )

        # Fallback
        return str(content).strip()

    def generate_with_gemini(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a plain-text response using Gemini.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        def operation():
            return self.llm.invoke(prompt)

        try:
            response = retry_operation(
                operation,
                max_attempts=3,
                delay=2,
            )

            content = getattr(
                response,
                "content",
                None,
            )

            if content is None:
                raise RuntimeError(
                    "Gemini returned an invalid response."
                )

            text = self._extract_text(content)

            if not text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text

        except Exception as exc:
            logger.exception(
                "Gemini service request failed."
            )

            raise RuntimeError(
                f"Gemini service failed: {exc}"
            ) from exc