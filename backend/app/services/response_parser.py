import re

from app.utils.helpers import is_valid_text


VALID_GRADES = {"A", "B", "C", "D"}


def extract_grade(feedback: str) -> str:
    """Extract a valid A-D grade from Gemini's response."""

    if not is_valid_text(feedback):
        return ""

    match = re.search(
        r"\bGrade\s*[:\-]?\s*([ABCD])\b",
        feedback,
        re.IGNORECASE,
    )

    if match:
        grade = match.group(1).upper()

        if grade in VALID_GRADES:
            return grade

    return ""