import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config.env"

# Load the project's config.env explicitly.
load_dotenv(CONFIG_FILE, override=True)


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv(
            "APP_NAME",
            "HealthBot",
        )

        self.app_version = os.getenv(
            "APP_VERSION",
            "1.0.0",
        )

        self.environment = os.getenv(
            "ENVIRONMENT",
            "development",
        )

        self.allowed_origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3030",
        )

        self.max_topic_length = int(
            os.getenv(
                "MAX_TOPIC_LENGTH",
                "200",
            )
        )

        self.max_answer_length = int(
            os.getenv(
                "MAX_ANSWER_LENGTH",
                "2000",
            )
        )

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_api_keys = os.getenv(
            "GEMINI_API_KEYS"
        )

        self.tavily_api_key = os.getenv(
            "TAVILY_API_KEY"
        )

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
            keys.append(
                self.gemini_api_key.strip()
            )

        if self.gemini_api_keys:
            keys.extend(
                key.strip()
                for key in self.gemini_api_keys.split(",")
                if key.strip()
            )

        return list(dict.fromkeys(keys))


settings = Settings()