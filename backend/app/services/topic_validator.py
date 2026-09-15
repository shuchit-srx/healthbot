import re

from rapidfuzz import fuzz, process

from app.core.health_vocabulary import HEALTH_TOPICS
from app.core.prompts import TOPIC_CLASSIFICATION_PROMPT
from app.services.gemini import GeminiService
from app.utils.helpers import format_prompt, is_valid_text


FUZZY_THRESHOLD = 85


class TopicValidator:

    def __init__(self):
        self.gemini_service = GeminiService()

    def normalize_topic(self, topic: str) -> str:
        """Normalize user input for topic comparison."""

        if not topic:
            return ""

        topic = topic.lower().strip()
        topic = re.sub(r"[-_/]", " ", topic)
        topic = re.sub(r"\s+", " ", topic)

        return topic

    def exact_health_match(self, topic: str) -> bool:
        """Check for an exact match in the local health vocabulary."""

        normalized_topic = self.normalize_topic(topic)

        return normalized_topic in HEALTH_TOPICS

    def fuzzy_health_match(self, topic: str):
        """Find a close match for spelling mistakes and minor variations."""

        normalized_topic = self.normalize_topic(topic)

        if not normalized_topic:
            return None, 0

        result = process.extractOne(
            normalized_topic,
            list(HEALTH_TOPICS),
            scorer=fuzz.ratio,
        )

        if result is None:
            return None, 0

        matched_topic, score, _ = result

        if score >= FUZZY_THRESHOLD:
            return matched_topic, score

        return None, score

    def classify_with_gemini(self, topic: str):
        """Use Gemini as the final validation and correction fallback."""

        if not is_valid_text(topic):
            return False, ""

        prompt = format_prompt(
            TOPIC_CLASSIFICATION_PROMPT,
            topic=topic,
        )

        try:
            response = self.gemini_service.generate_with_gemini(prompt)

            classification_match = re.search(
                r"Classification:\s*(HEALTH|NON_HEALTH)",
                response,
                re.IGNORECASE,
            )

            corrected_match = re.search(
                r"Corrected Topic:\s*(.+)",
                response,
                re.IGNORECASE,
            )

            if not classification_match:
                return False, ""

            classification = classification_match.group(1).upper()

            corrected_topic = ""

            if corrected_match:
                corrected_topic = self.normalize_topic(
                    corrected_match.group(1)
                )

            if classification == "HEALTH":
                return True, corrected_topic

            return False, ""

        except Exception:
            return False, ""

    def validate_health_topic(self, topic: str) -> tuple[bool, str]:
        """
        Validate and normalize a user-provided health topic.

        Validation order:
        1. Exact match
        2. Fuzzy match
        3. Gemini classification and spelling correction
        """

        if not is_valid_text(topic):
            return False, ""

        normalized_topic = self.normalize_topic(topic)

        # 1. Exact match
        if self.exact_health_match(normalized_topic):
            return True, normalized_topic

        # 2. Fuzzy match
        fuzzy_match, _ = self.fuzzy_health_match(
            normalized_topic
        )

        if fuzzy_match is not None:
            return True, fuzzy_match

        # 3. Gemini fallback
        is_health_topic, corrected_topic = (
            self.classify_with_gemini(normalized_topic)
        )

        if is_health_topic and corrected_topic:
            return True, corrected_topic

        return False, ""