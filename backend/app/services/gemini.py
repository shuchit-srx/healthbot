from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.utils.helpers import is_valid_text
from app.utils.retry import retry_operation


class GeminiService:

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=settings.gemini_api_key,
        )

    def generate_with_gemini(self, prompt: str) -> str:
        """Generate and validate text output from Gemini."""

        if not is_valid_text(prompt):
            raise ValueError("Prompt cannot be empty.")

        def generate():
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

                            if value:
                                text_parts.append(value)

                text = "\n".join(text_parts).strip()

            else:
                text = str(content).strip()

            if not text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return text

        return retry_operation(generate)