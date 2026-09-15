from pydantic import BaseModel, Field


class HealthTopicRequest(BaseModel):
    """Request model for submitting a health topic."""

    topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Health topic the user wants to learn about.",
    )


class QuizAnswerRequest(BaseModel):
    """Request model for submitting a quiz answer."""

    user_answer: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's answer to the comprehension question.",
    )


class SessionDecisionRequest(BaseModel):
    """Request model for continuing or ending a session."""

    continue_session: bool