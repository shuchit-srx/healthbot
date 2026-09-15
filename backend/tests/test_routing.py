from app.graph.workflow import (
    route_after_grading,
    route_after_quiz,
    route_after_search,
    route_after_session,
    route_after_summary,
    route_after_validation,
)


def test_validation_routes_to_search():
    assert route_after_validation(
        {"topic": "diabetes"}
    ) == "search"


def test_validation_error_routes_to_end():
    assert route_after_validation(
        {"error": "Invalid topic"}
    ) == "end"


def test_search_routes_to_summary():
    assert route_after_search(
        {
            "search_results": [
                {"content": "Medical information"}
            ]
        }
    ) == "summarize"


def test_search_error_routes_to_end():
    assert route_after_search(
        {"error": "Search failed"}
    ) == "end"


def test_summary_routes_to_quiz():
    assert route_after_summary(
        {
            "summary": "Medical information"
        }
    ) == "generate_quiz"


def test_summary_error_routes_to_end():
    assert route_after_summary(
        {"error": "Summary failed"}
    ) == "end"


def test_quiz_routes_to_grading():
    assert route_after_quiz(
        {
            "quiz_question": "What is diabetes?"
        }
    ) == "grade_answer"


def test_quiz_error_routes_to_end():
    assert route_after_quiz(
        {"error": "Quiz failed"}
    ) == "end"


def test_grading_routes_to_session():
    assert route_after_grading(
        {
            "quiz_completed": True
        }
    ) == "session_decision"


def test_grading_error_routes_to_end():
    assert route_after_grading(
        {"error": "Grading failed"}
    ) == "end"


def test_session_continue():
    assert route_after_session(
        {
            "continue_session": True
        }
    ) == "validate_topic"


def test_session_end():
    assert route_after_session(
        {
            "continue_session": False
        }
    ) == "end"