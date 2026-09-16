from itertools import cycle
from typing import Iterator

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

        # Keep a normal list for key rotation.
        self.api_keys = list(
            settings.gemini_api_keys
        )

        self._key_index = 0

        self.llm = self._create_llm()

    def _create_llm(self):
        """Create a Gemini client using the current API key."""

        api_key = self.api_keys[
            self._key_index
            % len(self.api_keys)
        ]

        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=api_key,
        )

    def _switch_to_next_key(self):
        """Switch Gemini client to the next configured API key."""

        if len(self.api_keys) <= 1:
            return

        self._key_index = (
            self._key_index + 1
        ) % len(self.api_keys)

        self.llm = self._create_llm()

        logger.warning(
            "Switched to the next Gemini API key."
        )

    @staticmethod
    def _extract_text(content) -> str:
        """
        Convert Gemini/LangChain response content
        into plain text.
        """

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text = item.get(
                            "text",
                            "",
                        )

                        if isinstance(text, str):
                            text_parts.append(text)

                elif isinstance(item, str):
                    text_parts.append(item)

            return "\n".join(
                part.strip()
                for part in text_parts
                if part.strip()
            )

        return str(content).strip()

    def generate_with_gemini(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a complete plain-text response.

        Each configured API key gets a chance to
        serve the request. Temporary failures are
        retried before moving to the next key.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        total_keys = len(
            self.api_keys
        )

        last_error = None

        for key_attempt in range(
            total_keys
        ):
            def operation():
                return self.llm.invoke(
                    prompt
                )

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

                text = self._extract_text(
                    content
                )

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text

            except Exception as exc:
                last_error = exc

                logger.warning(
                    "Gemini request failed with "
                    "API key %d/%d.",
                    key_attempt + 1,
                    total_keys,
                )

                if (
                    key_attempt
                    < total_keys - 1
                ):
                    self._switch_to_next_key()

        logger.exception(
            "Gemini service failed with all configured API keys."
        )

        raise RuntimeError(
            f"Gemini service failed: "
            f"all {total_keys} API keys failed: "
            f"{last_error}"
        ) from last_error

    def stream_with_gemini(
        self,
        prompt: str,
    ) -> Iterator[str]:
        """
        Stream Gemini response chunks.

        Each yielded value contains plain text.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:
            for chunk in self.llm.stream(
                prompt
            ):
                content = getattr(
                    chunk,
                    "content",
                    None,
                )

                if content is None:
                    continue

                text = self._extract_text(
                    content
                )

                if text:
                    yield text

        except Exception as exc:
            logger.exception(
                "Gemini streaming request failed."
            )

            raise RuntimeError(
                f"Gemini streaming failed: {exc}"
            ) from exc