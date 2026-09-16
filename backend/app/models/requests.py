from pydantic import BaseModel, Field


class HealthTopicRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )


class QuizAnswerRequest(BaseModel):
    user_answer: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class SessionDecisionRequest(BaseModel):
    continue_session: bool