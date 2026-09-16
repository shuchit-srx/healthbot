from collections.abc import Iterator
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.utils.retry import retry_operation


class GeminiService:
    def __init__(self) -> None:
        self.api_keys = settings.gemini_keys

        if not self.api_keys:
            raise ValueError("No Gemini API keys configured.")

        self.current_key_index = 0
        self.llm = self._create_llm(self.api_keys[self.current_key_index])

    def _create_llm(self, api_key: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=api_key,
            temperature=0.2,
        )

    def _switch_key(self) -> None:
        if self.current_key_index + 1 >= len(self.api_keys):
            return

        self.current_key_index += 1
        self.llm = self._create_llm(
            self.api_keys[self.current_key_index]
        )

    @staticmethod
    def _extract_text(response: Any) -> str:
        if response is None:
            return ""

        if isinstance(response, str):
            return response.strip()

        if isinstance(response, list):
            parts: list[str] = []

            for item in response:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)

            return "".join(parts).strip()

        content = getattr(response, "content", None)

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            return GeminiService._extract_text(content)

        text = getattr(response, "text", None)

        if isinstance(text, str):
            return text.strip()

        return ""

    def generate_with_gemini(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        last_error: Exception | None = None

        for _ in range(len(self.api_keys)):
            try:
                response = retry_operation(
                    lambda: self.llm.invoke(prompt),
                    max_attempts=3,
                    delay=2,
                )

                text = self._extract_text(response)

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text

            except Exception as error:
                last_error = error

                if self.current_key_index + 1 < len(self.api_keys):
                    self._switch_key()
                else:
                    break

        raise RuntimeError(
            f"Gemini service failed: all {len(self.api_keys)} API keys exhausted."
        ) from last_error

    def stream_with_gemini(self, prompt: str) -> Iterator[str]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        last_error: Exception | None = None

        for _ in range(len(self.api_keys)):
            try:
                chunks = retry_operation(
                    lambda: self.llm.stream(prompt),
                    max_attempts=3,
                    delay=2,
                )

                for chunk in chunks:
                    text = self._extract_text(chunk)

                    if text:
                        yield text

                return

            except Exception as error:
                last_error = error

                if self.current_key_index + 1 < len(self.api_keys):
                    self._switch_key()
                else:
                    break

        raise RuntimeError(
            f"Gemini service failed: all {len(self.api_keys)} API keys exhausted."
        ) from last_error