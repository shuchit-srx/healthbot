import re

from app.core.logging import get_logger
from app.utils.helpers import is_valid_text


logger = get_logger(__name__)

VALID_GRADES = {"A", "B", "C", "D"}


def extract_grade(feedback: str) -> str:
    """Extract a valid A-D grade from Gemini feedback."""

    if not is_valid_text(feedback):
        return ""

    match = re.search(
        r"\bGrade\s*[:\-]?\s*([ABCD])\b",
        feedback,
        re.IGNORECASE,
    )

    if not match:
        logger.warning(
            "Unable to extract a valid grade from Gemini response."
        )
        return ""

    grade = match.group(1).upper()

    if grade not in VALID_GRADES:
        return ""

    return grade


def extract_section(
    response: str,
    section_name: str,
) -> str:
    """Extract a named section from a structured Gemini response."""

    if not is_valid_text(response):
        return ""

    if not is_valid_text(section_name):
        return ""

    pattern = (
        rf"{re.escape(section_name)}\s*:\s*"
        rf"(.*?)(?=\n[A-Za-z ]+\s*:|$)"
    )

    match = re.search(
        pattern,
        response,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    return match.group(1).strip()