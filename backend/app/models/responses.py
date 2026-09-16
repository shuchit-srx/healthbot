from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class HealthTopicResponse(BaseModel):
    valid: bool
    topic: str | None = None
    message: str | None = None


class TopicValidationResponse(BaseModel):
    valid: bool
    topic: str | None = None
    message: str | None = None


class SummaryResponse(BaseModel):
    topic: str
    summary: str
    sources: list[Any] = Field(
        default_factory=list
    )


class QuizResponse(BaseModel):
    question: str


class GradeResponse(BaseModel):
    grade: str
    feedback: str


class SessionResponse(BaseModel):
    continue_session: bool


class HealthBotStateResponse(BaseModel):
    topic: str | None = None

    search_results: list[Any] = Field(
        default_factory=list
    )

    summary: str | None = None

    quiz_question: str | None = None

    user_answer: str | None = None

    grade: str | None = None

    feedback: str | None = None

    ready_for_quiz: bool = False

    quiz_completed: bool = False

    continue_session: bool = False

    error: str | None = None