from typing import Iterator
import json

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.core.prompts import SUMMARY_PROMPT
from app.models.requests import HealthTopicRequest
from app.models.responses import SummaryResponse
from app.services.gemini import GeminiService
from app.services.tavily import TavilyService
from app.utils.helpers import format_prompt


router = APIRouter(
    prefix="/api/education",
    tags=["Education"],
)


tavily_service = TavilyService()
gemini_service = GeminiService()


@router.post(
    "/summary",
    response_model=SummaryResponse,
)
async def generate_summary(
    request: HealthTopicRequest,
) -> SummaryResponse:
    results = await run_in_threadpool(
        tavily_service.search_medical_information,
        request.topic,
    )

    prompt = format_prompt(
        SUMMARY_PROMPT,
        topic=request.topic,
        search_results=results,
    )

    summary = await run_in_threadpool(
        gemini_service.generate_with_gemini,
        prompt,
    )

    return SummaryResponse(
        topic=request.topic,
        summary=summary,
        sources=results,
    )


@router.post(
    "/summary/stream",
)
async def stream_summary(
    request: HealthTopicRequest,
) -> StreamingResponse:
    results = await run_in_threadpool(
        tavily_service.search_medical_information,
        request.topic,
    )

    prompt = format_prompt(
        SUMMARY_PROMPT,
        topic=request.topic,
        search_results=results,
    )

    def generate() -> Iterator[str]:
        try:
            for chunk in (
                gemini_service.stream_with_gemini(
                    prompt
                )
            ):
                yield (
                    json.dumps(
                        {
                            "type": "chunk",
                            "content": chunk,
                        }
                    )
                    + "\n"
                )

            yield (
                json.dumps(
                    {
                        "type": "done",
                    }
                )
                + "\n"
            )

        except Exception:
            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message": (
                            "Unable to complete "
                            "the response. "
                            "Please try again."
                        ),
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        generate(),
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )