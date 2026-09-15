import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load environment variables
load_dotenv("config.env")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    tavily_api_key: str


def get_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    # Validate required API credentials
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Check your config.env file."
        )

    if not tavily_api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing. Check your config.env file."
        )

    return Settings(
        gemini_api_key=gemini_api_key,
        tavily_api_key=tavily_api_key,
    )


settings = get_settings()