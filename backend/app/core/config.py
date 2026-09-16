import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv("config.env")


class Settings(BaseModel):
    gemini_api_keys: list[str] = []
    tavily_api_key: str = ""
    allowed_origins: list[str] = [
        "http://localhost:3000"
    ]
    max_topic_length: int = 200
    max_answer_length: int = 2000


def _get_gemini_keys() -> list[str]:
    keys = []

    for name, value in os.environ.items():
        if name.startswith(
            "GEMINI_API_KEY"
        ) and value.strip():
            keys.append(value.strip())

    primary = os.getenv(
        "GEMINI_API_KEY"
    )

    if (
        primary
        and primary.strip()
        and primary.strip() not in keys
    ):
        keys.insert(
            0,
            primary.strip(),
        )

    return keys


def _get_allowed_origins() -> list[str]:
    value = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000",
    )

    return [
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    ]


settings = Settings(
    gemini_api_keys=_get_gemini_keys(),
    tavily_api_key=os.getenv(
        "TAVILY_API_KEY",
        "",
    ),
    allowed_origins=_get_allowed_origins(),
)