import re

from rapidfuzz import fuzz, process

from app.core.health_vocabulary import HEALTH_TOPICS
from app.core.logging import get_logger
from app.core.prompts import TOPIC_CLASSIFICATION_PROMPT
from app.services.gemini import GeminiService
from app.utils.helpers import format_prompt, is_valid_text


logger = get_logger(__name__)

FUZZY_THRESHOLD = 85


class TopicValidator:
    """Validate and normalize user-provided health topics."""

    def __init__(self):
        self.gemini_service = GeminiService()

    def normalize_topic(self, topic: str) -> str:
        """Normalize topic text for comparison."""

        if not is_valid_text(topic):
            return ""

        normalized = topic.lower().strip()
        normalized = re.sub(r"[-_/]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized)

        return normalized

    def exact_health_match(self, topic: str) -> bool:
        """Check whether a topic exactly matches the health vocabulary."""

        normalized_topic = self.normalize_topic(topic)

        return normalized_topic in HEALTH_TOPICS

    def fuzzy_health_match(
        self,
        topic: str,
    ) -> tuple[str | None, float]:
        """Find a close health-topic match."""

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

    def classify_with_gemini(
        self,
        topic: str,
    ) -> tuple[bool, str]:
        """Use Gemini as a fallback health-topic classifier."""

        if not is_valid_text(topic):
            return False, ""

        prompt = format_prompt(
            TOPIC_CLASSIFICATION_PROMPT,
            topic=topic,
        )

        try:
            response = self.gemini_service.generate_with_gemini(
                prompt
            )

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
                logger.warning(
                    "Gemini returned an invalid classification response."
                )
                return False, ""

            classification = classification_match.group(1).upper()

            if classification != "HEALTH":
                return False, ""

            corrected_topic = ""

            if corrected_match:
                corrected_topic = self.normalize_topic(
                    corrected_match.group(1)
                )

            if corrected_topic == "none":
                corrected_topic = ""

            return bool(corrected_topic), corrected_topic

        except Exception:
            logger.exception(
                "Gemini topic classification failed."
            )
            return False, ""

    def validate_health_topic(
        self,
        topic: str,
    ) -> tuple[bool, str]:
        """
        Validate and normalize a health topic.

        Validation order:
        1. Exact match
        2. Fuzzy match
        3. Gemini classification
        """

        if not is_valid_text(topic):
            return False, ""

        normalized_topic = self.normalize_topic(topic)

        # 1. Exact match
        if self.exact_health_match(normalized_topic):
            logger.debug(
                "Topic validated using exact match: %s",
                normalized_topic,
            )
            return True, normalized_topic

        # 2. Fuzzy match
        fuzzy_match, fuzzy_score = self.fuzzy_health_match(
            normalized_topic
        )

        if fuzzy_match is not None:
            logger.debug(
                "Topic validated using fuzzy match: %s (%.1f)",
                fuzzy_match,
                fuzzy_score,
            )
            return True, fuzzy_match

        # 3. Gemini fallback
        logger.debug(
            "Using Gemini fallback for topic: %s",
            normalized_topic,
        )

        is_health_topic, corrected_topic = (
            self.classify_with_gemini(normalized_topic)
        )

        if is_health_topic and corrected_topic:
            return True, corrected_topic

        return False, ""