import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config.env"

load_dotenv(CONFIG_FILE, override=True)


class Settings:
    app_name: str = os.getenv("APP_NAME", "HealthBot")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")

    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000",
    )

    max_topic_length: int = int(
        os.getenv("MAX_TOPIC_LENGTH", "200")
    )

    max_answer_length: int = int(
        os.getenv("MAX_ANSWER_LENGTH", "2000")
    )

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_api_keys: str | None = os.getenv("GEMINI_API_KEYS")
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def gemini_keys(self) -> list[str]:
        keys: list[str] = []

        if self.gemini_api_key:
            keys.append(self.gemini_api_key.strip())

        if self.gemini_api_keys:
            keys.extend(
                key.strip()
                for key in self.gemini_api_keys.split(",")
                if key.strip()
            )

        return list(dict.fromkeys(keys))


settings = Settings()