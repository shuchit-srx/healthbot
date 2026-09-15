import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.core.exceptions import ConfigurationError


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / "config.env"

load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    environment: str
    debug: bool
    gemini_api_key: str
    tavily_api_key: str


def get_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if not gemini_api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing. Check backend/config.env."
        )

    if not tavily_api_key:
        raise ConfigurationError(
            "TAVILY_API_KEY is missing. Check backend/config.env."
        )

    environment = os.getenv(
        "ENVIRONMENT",
        "development",
    ).strip().lower()

    debug = os.getenv(
        "DEBUG",
        "false",
    ).strip().lower() in {"true", "1", "yes"}

    return Settings(
        app_name=os.getenv("APP_NAME", "HealthBot"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=environment,
        debug=debug,
        gemini_api_key=gemini_api_key,
        tavily_api_key=tavily_api_key,
    )


settings = get_settings()