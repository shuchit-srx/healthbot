from typing import Any

from pydantic import BaseModel, Field


class HealthTopicResponse(BaseModel):
    """Response returned after health-topic validation."""

    valid: bool
    topic: str = ""
    error: str = ""


class SearchResultResponse(BaseModel):
    """Medical source returned by the search service."""

    title: str = ""
    url: str = ""
    content: str = ""
    score: float = 0.0


class SummaryResponse(BaseModel):
    """Patient-friendly health information response."""

    topic: str
    summary: str
    sources: list[SearchResultResponse] = Field(default_factory=list)


class QuizResponse(BaseModel):
    """Generated comprehension question."""

    question: str


class GradeResponse(BaseModel):
    """Quiz grading result."""

    grade: str
    feedback: str


class HealthBotErrorResponse(BaseModel):
    """Standard API error response."""

    error: str
    detail: str = ""


class HealthBotStateResponse(BaseModel):
    """Serializable representation of workflow state."""

    data: dict[str, Any] = Field(default_factory=dict)