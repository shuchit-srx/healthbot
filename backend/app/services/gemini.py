from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini."""

    def __init__(self) -> None:
        self.api_keys = settings.gemini_api_keys

        if not self.api_keys:
            raise ValueError(
                "At least one Gemini API key is required."
            )

        self.current_key_index = 0

        self.llm = self._create_llm(
            self.api_keys[self.current_key_index]
        )

    def _create_llm(
        self,
        api_key: str,
    ) -> ChatGoogleGenerativeAI:
        """Create a Gemini client using the provided API key."""

        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=api_key,
        )

    def _switch_to_next_key(self) -> bool:
        """Switch to the next available Gemini API key."""

        if (
            self.current_key_index
            >= len(self.api_keys) - 1
        ):
            return False

        self.current_key_index += 1

        self.llm = self._create_llm(
            self.api_keys[self.current_key_index]
        )

        logger.warning(
            "Switched to Gemini API key %s.",
            self.current_key_index + 1,
        )

        return True

    def generate_with_gemini(
        self,
        prompt: str,
    ) -> str:
        """Generate a response using Gemini with key fallback."""

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        total_keys = len(self.api_keys)

        for attempt in range(total_keys):
            try:
                logger.info(
                    "Calling Gemini using API key %s/%s.",
                    self.current_key_index + 1,
                    total_keys,
                )

                response = self.llm.invoke(prompt)

                content = getattr(
                    response,
                    "content",
                    None,
                )

                if not content or not str(content).strip():
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return str(content).strip()

            except Exception as exc:
                logger.warning(
                    "Gemini API key %s failed: %s",
                    self.current_key_index + 1,
                    exc,
                )

                if not self._switch_to_next_key():
                    logger.exception(
                        "All Gemini API keys failed."
                    )

                    raise RuntimeError(
                        "Gemini service failed after "
                        f"trying all {total_keys} API keys."
                    ) from exc

        raise RuntimeError(
            "Gemini service failed."
        )