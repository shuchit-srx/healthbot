from app.core.prompts import SUMMARY_PROMPT
from app.graph.state import HealthBotState
from app.services.gemini import GeminiService
from app.services.tavily import TavilyService
from app.services.topic_validator import TopicValidator
from app.utils.helpers import format_prompt, is_valid_text
from app.core.prompts import QUIZ_PROMPT
from app.core.prompts import GRADING_PROMPT
from app.services.response_parser import extract_grade
from app.utils.state_helpers import reset_state


topic_validator = TopicValidator()
tavily_service = TavilyService()
gemini_service = GeminiService()


def get_topic(state: HealthBotState) -> HealthBotState:
    """Get and validate a health topic from the user."""

    while True:
        topic = input(
            "\nWhat health topic or medical condition "
            "would you like to learn about?\n> "
        ).strip()

        if not topic:
            print("Please enter a health topic.")
            continue

        is_valid, corrected_topic = (
            topic_validator.validate_health_topic(topic)
        )

        if not is_valid:
            print(
                "\nThe topic does not appear to be "
                "health-related."
            )
            print("Please enter a medical or health topic.")
            continue

        final_topic = corrected_topic or topic

        if final_topic.lower() != topic.lower():
            print(f"\nCorrected health topic: {final_topic}")
        else:
            print(f"\nHealth topic accepted: {final_topic}")

        return {
            "topic": final_topic,
            "error": "",
        }


def search_node(state: HealthBotState) -> HealthBotState:
    """Search for medical information using the validated topic."""

    topic = state.get("topic", "")

    if not is_valid_text(topic):
        return {
            "search_results": [],
            "error": "Health topic is missing.",
        }

    try:
        results = tavily_service.search_medical_information(topic)

        if not results:
            return {
                "search_results": [],
                "error": "No medical information found.",
            }

        return {
            "search_results": results,
            "error": "",
        }

    except Exception as e:
        return {
            "search_results": [],
            "error": f"Medical search failed: {e}",
        }


def summarize_information(state: HealthBotState) -> HealthBotState:
    """Generate a patient-friendly summary from medical search results."""

    topic = state.get("topic", "")
    search_results = state.get("search_results", [])

    if not is_valid_text(topic):
        return {
            "summary": "",
            "error": "Health topic is missing.",
        }

    if not isinstance(search_results, list) or not search_results:
        return {
            "summary": "",
            "error": "No medical information available for summarization.",
        }

    formatted_results = []

    for result in search_results:
        if not isinstance(result, dict):
            continue

        content = result.get("content", "")

        if not is_valid_text(content):
            continue

        formatted_results.append(
            f"Title: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {content}"
        )

    if not formatted_results:
        return {
            "summary": "",
            "error": "Search results contain no usable information.",
        }

    search_context = "\n\n".join(formatted_results)

    prompt = format_prompt(
        SUMMARY_PROMPT,
        topic=topic,
        search_results=search_context,
    )

    try:
        summary = gemini_service.generate_with_gemini(prompt)

        if not is_valid_text(summary):
            return {
                "summary": "",
                "error": "Gemini returned an empty summary.",
            }

        return {
            "summary": summary.strip(),
            "error": "",
        }

    except Exception as e:
        return {
            "summary": "",
            "error": f"Summarization failed: {e}",
        }


def display_summary(state: HealthBotState) -> HealthBotState:
    """Display the summary and ask whether to continue to the quiz."""

    summary = state.get("summary", "").strip()

    if not summary:
        return {
            "ready_for_quiz": False,
            "error": "Summary is unavailable.",
        }

    print("\n" + "=" * 60)
    print("HEALTH INFORMATION")
    print("=" * 60)
    print(summary)
    print("=" * 60)

    while True:
        response = input(
            "\nAre you ready for the comprehension check? (yes/no)\n> "
        ).strip().lower()

        if response in {"yes", "y"}:
            return {
                "ready_for_quiz": True,
                "error": "",
            }

        if response in {"no", "n"}:
            return {
                "ready_for_quiz": False,
                "error": "",
            }

        print("Invalid input. Please enter yes or no.")

def route_quiz(state: HealthBotState) -> str:
    """Route the workflow based on whether the user wants the quiz."""

    if state.get("ready_for_quiz", False):
        return "generate_quiz"

    return "session_decision"

def generate_quiz(state: HealthBotState) -> HealthBotState:
    """Generate one comprehension question based only on the summary."""

    summary = state.get("summary", "")

    if not is_valid_text(summary):
        return {
            "quiz_question": "",
            "ready_for_quiz": False,
            "error": "Summary is missing. Cannot generate quiz.",
        }

    prompt = format_prompt(
        QUIZ_PROMPT,
        summary=summary,
    )

    try:
        question = gemini_service.generate_with_gemini(prompt)

        if not is_valid_text(question):
            return {
                "quiz_question": "",
                "ready_for_quiz": False,
                "error": "Gemini returned an empty quiz question.",
            }

        return {
            "quiz_question": question.strip(),
            "ready_for_quiz": True,
            "error": "",
        }

    except Exception as e:
        return {
            "quiz_question": "",
            "ready_for_quiz": False,
            "error": f"Quiz generation failed: {e}",
        }

def get_quiz_answer(state: HealthBotState) -> HealthBotState:
    """Collect the user's answer to the generated quiz question."""

    question = state.get("quiz_question", "")

    if not is_valid_text(question):
        return {
            "user_answer": "",
            "error": "Quiz question is missing.",
        }

    while True:
        answer = input(
            f"\nQuestion:\n{question}\n\nYour answer:\n> "
        ).strip()

        if not answer:
            print("Please provide an answer before continuing.")
            continue

        return {
            "user_answer": answer,
            "error": "",
        }

def grade_answer(state: HealthBotState) -> HealthBotState:
    """Grade the user's answer using only the generated summary."""

    topic = state.get("topic", "")
    summary = state.get("summary", "")
    quiz_question = state.get("quiz_question", "")
    user_answer = state.get("user_answer", "")

    if not is_valid_text(topic):
        return {
            "grade": "",
            "feedback": "",
            "error": "Health topic is missing.",
        }

    if not is_valid_text(summary):
        return {
            "grade": "",
            "feedback": "",
            "error": "Summary is missing.",
        }

    if not is_valid_text(quiz_question):
        return {
            "grade": "",
            "feedback": "",
            "error": "Quiz question is missing.",
        }

    if not is_valid_text(user_answer):
        return {
            "grade": "",
            "feedback": "",
            "error": "User answer is missing.",
        }

    prompt = format_prompt(
        GRADING_PROMPT,
        topic=topic,
        summary=summary,
        quiz_question=quiz_question,
        user_answer=user_answer,
    )

    try:
        grading_result = gemini_service.generate_with_gemini(prompt)

        if not is_valid_text(grading_result):
            return {
                "grade": "",
                "feedback": "",
                "error": "Gemini returned an empty grading response.",
            }

        grading_result = grading_result.strip()
        grade = extract_grade(grading_result)

        if not grade:
            return {
                "grade": "",
                "feedback": grading_result,
                "error": "Gemini returned an invalid grade format.",
            }

        return {
            "grade": grade,
            "feedback": grading_result,
            "quiz_completed": True,
            "error": "",
        }

    except Exception as e:
        return {
            "grade": "",
            "feedback": "",
            "quiz_completed": False,
            "error": f"Answer grading failed: {e}",
        }

def display_feedback(state: HealthBotState) -> HealthBotState:
    """Display the grading result and feedback to the user."""

    grade = state.get("grade", "")
    feedback = state.get("feedback", "")
    error = state.get("error", "")

    if error:
        print(f"\nUnable to evaluate your answer: {error}")
        return state

    if not is_valid_text(feedback):
        print("\nNo feedback was generated.")
        return {
            "error": "Feedback is unavailable.",
        }

    print("\n" + "=" * 50)
    print("QUIZ RESULT")
    print("=" * 50)

    if grade:
        print(f"\nGrade: {grade}")

    print("\nFeedback:")
    print(feedback)

    print("=" * 50)

    return state

def session_decision(state: HealthBotState) -> HealthBotState:
    """Ask whether the user wants to learn about another topic."""

    while True:
        choice = input(
            "\nWould you like to learn about another health topic? "
            "(yes/no)\n> "
        ).strip().lower()

        if choice in {"yes", "y"}:
            return {
                "continue_session": True,
                "error": "",
            }

        if choice in {"no", "n"}:
            return {
                "continue_session": False,
                "error": "",
            }

        print("Please enter 'yes' or 'no'.")

def reset_state_node(state: HealthBotState) -> HealthBotState:
    """Reset session state before starting a new topic."""

    return reset_state()

