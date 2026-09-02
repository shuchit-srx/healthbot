"""
Automated tests for the HealthBot application.

The HealthBot implementation is maintained in healthbot.ipynb.
These tests load the notebook definitions without running the
interactive application cell.

External AI and search services are mocked so the tests remain:
- Fast
- Deterministic
- Offline
- Safe from API usage
"""

from pathlib import Path
from unittest.mock import Mock, patch

import nbformat
import pytest


# ============================================================
# Load HealthBot definitions from the notebook
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "healthbot.ipynb"


def load_healthbot():
    """
    Load definitions from healthbot.ipynb without running
    the interactive application or visualization cells.
    """

    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(
            f"HealthBot notebook not found: {NOTEBOOK_PATH}"
        )

    notebook = nbformat.read(
        NOTEBOOK_PATH,
        as_version=4
    )

    namespace = {}

    for cell in notebook.cells:

        if cell.cell_type != "code":
            continue

        source = cell.source

        # Skip environment/API configuration.
        # Tests provide their own mocked configuration.
        if "load_dotenv(" in source:
            continue

        # Skip AI component initialization.
        if "gemini_llm = ChatGoogleGenerativeAI" in source:
            continue

        if "tavily_tool = TavilySearch" in source:
            continue

        # Skip standalone visualization cells.
        if "draw_mermaid()" in source:
            continue

        # Skip the final interactive application execution.
        if "healthbot_app.invoke(" in source:
            continue

        # Skip any notebook testing cells that may still exist.
        if (
            "Test initial/reset state" in source
            or "Test health-topic validation" in source
        ):
            continue

        exec(
            compile(
                source,
                str(NOTEBOOK_PATH),
                "exec"
            ),
            namespace
        )

    return namespace


@pytest.fixture(scope="session")
def hb():
    """Provide the loaded HealthBot definitions."""
    return load_healthbot()


# ============================================================
# Basic helper functions
# ============================================================

def test_is_valid_text(hb):

    assert hb["is_valid_text"]("diabetes") is True
    assert hb["is_valid_text"]("  diabetes  ") is True

    assert hb["is_valid_text"]("") is False
    assert hb["is_valid_text"]("   ") is False
    assert hb["is_valid_text"](None) is False
    assert hb["is_valid_text"](123) is False


def test_normalize_topic(hb):

    normalize_topic = hb["normalize_topic"]

    assert normalize_topic("Diabetes") == "diabetes"
    assert normalize_topic("  Diabetes  ") == "diabetes"
    assert normalize_topic("high-blood-pressure") == (
        "high blood pressure"
    )
    assert normalize_topic("heart_attack") == "heart attack"
    assert normalize_topic("  chest   pain ") == "chest pain"
    assert normalize_topic("") == ""


def test_exact_health_match(hb):

    exact_health_match = hb["exact_health_match"]

    assert exact_health_match("diabetes") is True
    assert exact_health_match("chest pain") is True
    assert exact_health_match("football") is False
    assert exact_health_match("car engine") is False


def test_fuzzy_health_match(hb):

    fuzzy_health_match = hb["fuzzy_health_match"]

    matched_topic, score = fuzzy_health_match("diabetees")

    assert matched_topic == "diabetes"
    assert score >= hb["FUZZY_THRESHOLD"]

    matched_topic, score = fuzzy_health_match("")

    assert matched_topic is None
    assert score == 0


def test_format_prompt(hb):

    format_prompt = hb["format_prompt"]

    prompt = format_prompt(
        "Explain {topic}.",
        topic="diabetes"
    )

    assert prompt == "Explain diabetes."


def test_format_prompt_missing_variable(hb):

    format_prompt = hb["format_prompt"]

    with pytest.raises(ValueError):
        format_prompt(
            "Explain {topic} and {missing}.",
            topic="diabetes"
        )


def test_format_prompt_empty_template(hb):

    format_prompt = hb["format_prompt"]

    with pytest.raises(ValueError):
        format_prompt("")


# ============================================================
# Grade extraction
# ============================================================

@pytest.mark.parametrize(
    "feedback, expected",
    [
        ("Grade: A", "A"),
        ("Grade: B\nExplanation: Mostly correct.", "B"),
        ("Grade: C", "C"),
        ("Grade: D", "D"),
        ("grade: a", "A"),
        ("GRADE: B", "B"),
        ("This is Grade: C based on the evidence.", "C"),
    ]
)
def test_extract_grade(hb, feedback, expected):

    assert hb["extract_grade"](feedback) == expected


@pytest.mark.parametrize(
    "feedback",
    [
        "",
        "No grade provided",
        "Grade: E",
        "Score: A",
        None,
    ]
)
def test_extract_grade_invalid(hb, feedback):

    assert hb["extract_grade"](feedback) == ""


# ============================================================
# Error state
# ============================================================

def test_create_error_state(hb):

    create_error_state = hb.get("create_error_state")

    if create_error_state is None:
        pytest.skip(
            "create_error_state is not used by the final application."
        )

    state = create_error_state("Test error")

    assert state == {
        "error": "Test error"
    }


# ============================================================
# Reset state
# ============================================================

def test_reset_state(hb):

    state = hb["reset_state"]()

    assert state["topic"] == ""
    assert state["search_results"] == []
    assert state["summary"] == ""
    assert state["quiz_question"] == ""
    assert state["user_answer"] == ""
    assert state["grade"] == ""
    assert state["feedback"] == ""
    assert state["ready_for_quiz"] is False
    assert state["continue_session"] is False
    assert state["error"] == ""


# ============================================================
# Gemini classification
# ============================================================

def test_classify_with_gemini_health_topic(hb):

    fake_response = """
Classification: HEALTH
Corrected Topic: diabetees
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_response
            )
        }
    ):

        is_health, corrected = (
            hb["classify_with_gemini"]("diabetees")
        )

    assert is_health is True
    assert corrected == "diabetees"


def test_classify_with_gemini_non_health_topic(hb):

    fake_response = """
Classification: NON_HEALTH
Corrected Topic: none
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_response
            )
        }
    ):

        is_health, corrected = (
            hb["classify_with_gemini"]("football")
        )

    assert is_health is False
    assert corrected == ""


def test_classify_with_gemini_invalid_response(hb):

    fake_response = "This is not a valid classification."

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_response
            )
        }
    ):

        is_health, corrected = (
            hb["classify_with_gemini"]("unknown topic")
        )

    assert is_health is False
    assert corrected == ""


# ============================================================
# Health-topic validation
# ============================================================

def test_validate_health_topic_exact_match(hb):

    is_valid, corrected = (
        hb["validate_health_topic"]("diabetes")
    )

    assert is_valid is True
    assert corrected == "diabetes"


def test_validate_health_topic_fuzzy_match(hb):

    is_valid, corrected = (
        hb["validate_health_topic"]("diabetees")
    )

    assert is_valid is True
    assert corrected == "diabetes"


def test_validate_health_topic_gemini_fallback(hb):

    fake_response = """
Classification: HEALTH
Corrected Topic: hypertension
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_response
            )
        }
    ):

        is_valid, corrected = (
            hb["validate_health_topic"](
                "some medical condition"
            )
        )

    assert is_valid is True
    assert corrected == "hypertension"


def test_validate_health_topic_rejects_non_health(hb):

    fake_response = """
Classification: NON_HEALTH
Corrected Topic: none
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_response
            )
        }
    ):

        is_valid, corrected = (
            hb["validate_health_topic"]("football")
        )

    assert is_valid is False
    assert corrected == ""


def test_validate_health_topic_empty_input(hb):

    is_valid, corrected = (
        hb["validate_health_topic"]("")
    )

    assert is_valid is False
    assert corrected == ""


# ============================================================
# Gemini helper
# ============================================================

def test_generate_with_gemini_string_response(hb):

    fake_llm = Mock()

    fake_response = Mock()
    fake_response.content = "Generated medical information."

    fake_llm.invoke.return_value = fake_response

    with patch.dict(
        hb,
        {"gemini_llm": fake_llm}
    ):

        result = hb["generate_with_gemini"](
            "Explain diabetes."
        )

    assert result == "Generated medical information."

    fake_llm.invoke.assert_called_once_with(
        "Explain diabetes."
    )


def test_generate_with_gemini_empty_response(hb):

    fake_llm = Mock()

    fake_response = Mock()
    fake_response.content = ""

    fake_llm.invoke.return_value = fake_response

    with patch.dict(
        hb,
        {"gemini_llm": fake_llm}
    ):

        with pytest.raises(RuntimeError):
            hb["generate_with_gemini"](
                "Explain diabetes."
            )


def test_generate_with_gemini_empty_prompt(hb):

    with pytest.raises(ValueError):
        hb["generate_with_gemini"]("")


# ============================================================
# Tavily search helper
# ============================================================

def test_search_medical_information(hb):

    fake_tavily = Mock()

    fake_tavily.invoke.return_value = {
        "results": [
            {
                "title": "Diabetes Information",
                "url": "https://example.com/diabetes",
                "content": "Diabetes is a medical condition.",
                "score": 0.95
            }
        ]
    }

    with patch.dict(
        hb,
        {"tavily_tool": fake_tavily}
    ):

        results = hb["search_medical_information"](
            "diabetes"
        )

    assert len(results) == 1
    assert results[0]["title"] == "Diabetes Information"
    assert results[0]["url"] == (
        "https://example.com/diabetes"
    )
    assert results[0]["content"] == (
        "Diabetes is a medical condition."
    )


def test_search_medical_information_empty_topic(hb):

    with pytest.raises(ValueError):
        hb["search_medical_information"]("")


def test_search_medical_information_invalid_response(hb):

    fake_tavily = Mock()

    fake_tavily.invoke.return_value = {
        "invalid": "response"
    }

    with patch.dict(
        hb,
        {"tavily_tool": fake_tavily}
    ):

        with pytest.raises(RuntimeError):
            hb["search_medical_information"](
                "diabetes"
            )


# ============================================================
# Search node
# ============================================================

def test_search_node_success(hb):

    fake_results = [
        {
            "title": "Diabetes",
            "url": "https://example.com",
            "content": "Medical information.",
            "score": 0.9
        }
    ]

    with patch.dict(
        hb,
        {
            "search_medical_information": Mock(
                return_value=fake_results
            )
        }
    ):

        result = hb["search_node"](
            {"topic": "diabetes"}
        )

    assert result["search_results"] == fake_results
    assert result["error"] == ""


def test_search_node_missing_topic(hb):

    result = hb["search_node"](
        {"topic": ""}
    )

    assert result["search_results"] == []
    assert result["error"] == (
        "Health topic is missing."
    )


def test_search_node_handles_failure(hb):

    with patch.dict(
        hb,
        {
            "search_medical_information": Mock(
                side_effect=Exception("Search failed")
            )
        }
    ):

        result = hb["search_node"](
            {"topic": "diabetes"}
        )

    assert result["search_results"] == []
    assert "Medical search failed" in result["error"]


# ============================================================
# Summary node
# ============================================================

def test_summarize_information_success(hb):

    fake_summary = (
        "Diabetes is a condition that affects "
        "blood glucose levels."
    )

    search_results = [
        {
            "title": "Diabetes",
            "url": "https://example.com",
            "content": "Diabetes affects blood glucose.",
            "score": 0.9
        }
    ]

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_summary
            )
        }
    ):

        result = hb["summarize_information"](
            {
                "topic": "diabetes",
                "search_results": search_results
            }
        )

    assert result["summary"] == fake_summary
    assert result["error"] == ""


def test_summarize_information_missing_topic(hb):

    result = hb["summarize_information"](
        {
            "topic": "",
            "search_results": []
        }
    )

    assert result["summary"] == ""
    assert result["error"] == (
        "Health topic is missing."
    )


def test_summarize_information_missing_search_results(hb):

    result = hb["summarize_information"](
        {
            "topic": "diabetes",
            "search_results": []
        }
    )

    assert result["summary"] == ""
    assert result["error"] == (
        "No medical information available for summarization."
    )


# ============================================================
# Quiz generation
# ============================================================

def test_generate_quiz_success(hb):

    fake_question = (
        "What does diabetes primarily affect?"
    )

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_question
            )
        }
    ):

        result = hb["generate_quiz"](
            {
                "summary": (
                    "Diabetes affects blood glucose levels."
                )
            }
        )

    assert result["quiz_question"] == fake_question
    assert result["ready_for_quiz"] is True
    assert result["error"] == ""


def test_generate_quiz_missing_summary(hb):

    result = hb["generate_quiz"](
        {
            "summary": ""
        }
    )

    assert result["quiz_question"] == ""
    assert result["ready_for_quiz"] is False
    assert "Summary is missing" in result["error"]


# ============================================================
# Quiz routing
# ============================================================

def test_route_quiz_to_generation(hb):

    result = hb["route_quiz"](
        {
            "ready_for_quiz": True
        }
    )

    assert result == "generate_quiz"


def test_route_quiz_when_user_skips_quiz(hb):

    result = hb["route_quiz"](
        {
            "ready_for_quiz": False
        }
    )

    assert result == "session_decision"


def test_route_quiz_missing_flag(hb):

    result = hb["route_quiz"]({})

    assert result == "session_decision"


# ============================================================
# Grading node
# ============================================================

def test_grade_answer_success(hb):

    fake_feedback = """
Grade: A

Explanation:
The answer correctly identifies the key concept.

Evidence:
The summary states that diabetes affects blood glucose.

Source:
Medical source
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_feedback
            )
        }
    ):

        result = hb["grade_answer"](
            {
                "topic": "diabetes",
                "summary": (
                    "Diabetes affects blood glucose levels."
                ),
                "quiz_question": (
                    "What does diabetes affect?"
                ),
                "user_answer": (
                    "Blood glucose levels."
                )
            }
        )

    assert result["grade"] == "A"
    assert result["feedback"] == fake_feedback.strip()
    assert result["error"] == ""


def test_grade_answer_missing_answer(hb):

    result = hb["grade_answer"](
        {
            "topic": "diabetes",
            "summary": "Diabetes affects blood glucose.",
            "quiz_question": "What does diabetes affect?",
            "user_answer": ""
        }
    )

    assert result["grade"] == ""
    assert result["feedback"] == ""
    assert result["error"] == (
        "User answer is missing."
    )


def test_grade_answer_invalid_grade(hb):

    fake_feedback = """
Grade: E

Explanation:
Invalid grade.
"""

    with patch.dict(
        hb,
        {
            "generate_with_gemini": Mock(
                return_value=fake_feedback
            )
        }
    ):

        result = hb["grade_answer"](
            {
                "topic": "diabetes",
                "summary": "Diabetes affects blood glucose.",
                "quiz_question": "What does diabetes affect?",
                "user_answer": "Blood glucose."
            }
        )

    assert result["grade"] == ""
    assert result["feedback"] == fake_feedback.strip()
    assert "invalid grade" in result["error"].lower()


# ============================================================
# Session decision routing
# ============================================================

def test_route_session_continue(hb):

    result = hb["route_session"](
        {
            "continue_session": True
        }
    )

    assert result == "reset_state"


def test_route_session_end(hb):

    result = hb["route_session"](
        {
            "continue_session": False
        }
    )

    assert result == hb["END"]


# ============================================================
# Reset state node
# ============================================================

def test_reset_state_node(hb):

    result = hb["reset_state_node"](
        {
            "topic": "diabetes",
            "summary": "Old summary",
            "grade": "A"
        }
    )

    assert result["topic"] == ""
    assert result["summary"] == ""
    assert result["grade"] == ""
    assert result["ready_for_quiz"] is False
    assert result["continue_session"] is False


# ============================================================
# Topic input node
# ============================================================

def test_get_topic_accepts_valid_topic(hb):

    with patch(
        "builtins.input",
        return_value="diabetes"
    ):

        result = hb["get_topic"](
            {}
        )

    assert result["topic"] == "diabetes"
    assert result["error"] == ""


def test_get_topic_corrects_fuzzy_topic(hb):

    with patch(
        "builtins.input",
        return_value="diabetees"
    ):

        result = hb["get_topic"](
            {}
        )

    assert result["topic"] == "diabetes"
    assert result["error"] == ""


# ============================================================
# Workflow structure
# ============================================================

def test_workflow_nodes_registered(hb):

    graph = hb["healthbot_graph"]

    expected_nodes = {
        "get_topic",
        "search",
        "summarize",
        "display_summary",
        "generate_quiz",
        "get_quiz_answer",
        "grade_answer",
        "display_feedback",
        "session_decision",
        "reset_state",
    }

    actual_nodes = set(graph.nodes.keys())

    assert expected_nodes.issubset(actual_nodes)


def test_compiled_application_exists(hb):

    assert hb["healthbot_app"] is not None


def test_quiz_routing_is_present(hb):

    graph = hb["healthbot_graph"]

    graph_structure = graph.compile().get_graph()

    nodes = graph_structure.nodes

    assert "display_summary" in nodes
    assert "generate_quiz" in nodes
    assert "session_decision" in nodes


# ============================================================
# End-to-end node flow with mocked AI/search
# ============================================================

def test_basic_workflow_data_flow(hb):

    search_results = [
        {
            "title": "Diabetes Information",
            "url": "https://example.com/diabetes",
            "content": (
                "Diabetes is a condition that affects "
                "blood glucose levels."
            ),
            "score": 0.95
        }
    ]

    fake_summary = (
        "Diabetes affects blood glucose levels."
    )

    fake_question = (
        "What does diabetes affect?"
    )

    fake_feedback = """
Grade: A

Explanation:
The answer is correct.

Evidence:
Diabetes affects blood glucose levels.

Source:
Medical source
"""

    with patch.dict(
        hb,
        {
            "search_medical_information": Mock(
                return_value=search_results
            ),
            "generate_with_gemini": Mock(
                side_effect=[
                    fake_summary,
                    fake_question,
                    fake_feedback
                ]
            )
        }
    ):

        state = {
            "topic": "diabetes"
        }

        state.update(
            hb["search_node"](state)
        )

        assert state["search_results"] == search_results

        state.update(
            hb["summarize_information"](state)
        )

        assert state["summary"] == fake_summary

        state["ready_for_quiz"] = True

        route = hb["route_quiz"](state)

        assert route == "generate_quiz"

        state.update(
            hb["generate_quiz"](state)
        )

        assert state["quiz_question"] == fake_question

        state["user_answer"] = (
            "Blood glucose levels."
        )

        state.update(
            hb["grade_answer"](state)
        )

        assert state["grade"] == "A"
        assert state["error"] == ""