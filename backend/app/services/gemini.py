from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.helpers import is_valid_text
from app.utils.retry import retry_operation


logger = get_logger(__name__)


class GeminiService:
    """Service responsible for interacting with Google Gemini."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=settings.gemini_api_key,
        )

    def generate_with_gemini(self, prompt: str) -> str:
        """Generate validated text using Gemini with retry handling."""

        if not is_valid_text(prompt):
            raise ValueError("Prompt cannot be empty.")

        def generate() -> str:
            logger.debug("Sending request to Gemini.")

            response = self.llm.invoke(prompt)

            content = getattr(response, "content", None)

            if content is None:
                raise ValueError(
                    "Gemini returned no content."
                )

            if isinstance(content, str):
                text = content.strip()

            elif isinstance(content, list):
                text_parts = []

                for item in content:
                    if isinstance(item, str):
                        text_parts.append(item)

                    elif isinstance(item, dict):
                        if item.get("type") == "text":
                            value = item.get("text", "")

                            if is_valid_text(value):
                                text_parts.append(value)

                text = "\n".join(text_parts).strip()

            else:
                text = str(content).strip()

            if not text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            logger.debug("Gemini response received successfully.")

            return text

        try:
            return retry_operation(
                generate,
                max_attempts=3,
                delay=2,
            )

        except Exception as exc:
            logger.exception(
                "Gemini request failed after retries."
            )
            raise RuntimeError(
                f"Gemini service failed: {exc}"
            ) from exc