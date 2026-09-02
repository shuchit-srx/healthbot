"""
Automated tests for HealthBot.

The tests load functions from healthbot.ipynb and verify
the application's validation, state management, workflow
nodes, and routing behavior.

External Gemini and Tavily calls are mocked where necessary
so that unit tests remain fast and deterministic.
"""

import json
from pathlib import Path

import pytest

from nbformat import read
from nbconvert import PythonExporter


# ---------------------------------------------------------
# Load code from healthbot.ipynb
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "healthbot.ipynb"

def load_notebook_namespace():
    """
    Load HealthBot application code from the notebook.

    Executes:
    - imports
    - configuration
    - helpers
    - state
    - prompts
    - health-topic validation
    - workflow node definitions

    Skips:
    - manual tests
    - LangGraph construction
    - graph visualization
    - interactive execution
    """

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as file:
        notebook = read(file, as_version=4)

    namespace = {
        "__file__": str(NOTEBOOK_PATH),
        "__name__": "__notebook_test__",
    }

    # Required imports that the application code depends on.
    exec(
        """
import os
import re
import time
from typing import Any, TypedDict

import numpy as np

from dotenv import load_dotenv
from rapidfuzz import fuzz, process
from sentence_transformers import SentenceTransformer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
        """,
        namespace,
    )

    for cell in notebook.cells:

        if cell.cell_type != "code":
            continue

        source = cell.source.strip()

        if not source:
            continue

        # --------------------------------------------------
        # Skip manual test cells
        # --------------------------------------------------

        if (
            source.startswith("# Test")
            or source.startswith("# Testing")
            or source.startswith("# Run")
        ):
            continue

        # --------------------------------------------------
        # Skip interactive cells
        # --------------------------------------------------

        if "input(" in source:
            continue

        # --------------------------------------------------
        # Skip LangGraph construction and execution
        # --------------------------------------------------

        if any(
            text in source
            for text in [
                "healthbot_graph",
                "healthbot_app",
                "StateGraph(",
                "draw_mermaid",
            ]
        ):
            continue

        # --------------------------------------------------
        # Skip notebook imports because we already loaded
        # the required imports above.
        # --------------------------------------------------

        if source.startswith("import ") or source.startswith("from "):
            continue

        # --------------------------------------------------
        # Execute application code
        # --------------------------------------------------

        try:
            exec(source, namespace)

        except Exception as exc:
            raise RuntimeError(
                "Failed while loading notebook cell:\n\n"
                f"{source[:1000]}"
            ) from exc

    return namespace

@pytest.fixture(scope="module")
def app():
    """
    Load the HealthBot notebook once for the test module.
    """

    return load_notebook_namespace()

# ---------------------------------------------------------
# Helper Function Tests
# ---------------------------------------------------------


def test_is_valid_text(app):

    assert app["is_valid_text"]("hello") is True
    assert app["is_valid_text"]("  hello  ") is True

    assert app["is_valid_text"]("") is False
    assert app["is_valid_text"]("   ") is False
    assert app["is_valid_text"](None) is False


def test_normalize_topic(app):

    normalize_topic = app["normalize_topic"]

    assert normalize_topic(" Diabetes ") == "diabetes"

    assert normalize_topic("high-blood-pressure") == (
        "high blood pressure"
    )

    assert normalize_topic("  chest   pain ") == (
        "chest pain"
    )

    assert normalize_topic("") == ""

# ---------------------------------------------------------
# Health Topic Validation Tests
# ---------------------------------------------------------


def test_exact_health_match(app):

    exact_health_match = app["exact_health_match"]

    assert exact_health_match("diabetes") is True
    assert exact_health_match("chest pain") is True
    assert exact_health_match("football") is False


def test_fuzzy_health_match(app):

    fuzzy_health_match = app["fuzzy_health_match"]

    matched_topic, score = fuzzy_health_match(
        "diabetees"
    )

    assert matched_topic is not None
    assert score >= 85


def test_empty_health_topic(app):

    validate_health_topic = app["validate_health_topic"]

    assert validate_health_topic("") is False
    assert validate_health_topic("   ") is False

# ---------------------------------------------------------
# State Tests
# ---------------------------------------------------------


def test_reset_state(app):

    reset_state = app["reset_state"]

    state = reset_state()

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

# ---------------------------------------------------------
# Grade Extraction Tests
# ---------------------------------------------------------


def test_extract_grade(app):

    extract_grade = app["extract_grade"]

    assert extract_grade("Grade: A") == "A"
    assert extract_grade("Grade: B") == "B"
    assert extract_grade("Grade: C") == "C"
    assert extract_grade("Grade: D") == "D"

    assert extract_grade("Invalid response") == ""
    assert extract_grade("") == ""

# ---------------------------------------------------------
# Search Node Tests
# ---------------------------------------------------------


def test_search_node_empty_topic(app):

    search_node = app["search_node"]

    state = {
        "topic": "",
        "search_results": []
    }

    result = search_node(state)

    assert result["search_results"] == []

    assert result["error"] == (
        "Health topic is missing."
    )

def test_search_node_success(app, monkeypatch):

    search_node = app["search_node"]

    fake_results = [
        {
            "title": "Diabetes Information",
            "url": "https://example.com",
            "content": "Diabetes affects blood sugar.",
            "score": 0.95
        }
    ]

    monkeypatch.setitem(
        search_node.__globals__,
        "search_medical_information",
        lambda topic: fake_results
    )

    result = search_node(
        {
            "topic": "diabetes",
            "search_results": []
        }
    )

    assert result["error"] == ""
    assert len(result["search_results"]) == 1
    assert result["search_results"][0]["title"] == (
        "Diabetes Information"
    )

# ---------------------------------------------------------
# Summary Node Tests
# ---------------------------------------------------------


def test_summary_without_search_results(app):

    summarize_information = app[
        "summarize_information"
    ]

    result = summarize_information(
        {
            "topic": "diabetes",
            "search_results": []
        }
    )

    assert result["summary"] == ""

    assert result["error"] == (
        "No medical information available for summarization."
    )

def test_summary_success(app, monkeypatch):

    summarize_information = app[
        "summarize_information"
    ]

    fake_summary = (
        "Diabetes is a condition that affects "
        "blood sugar regulation."
    )

    monkeypatch.setitem(
        summarize_information.__globals__,
        "generate_with_gemini",
        lambda prompt: fake_summary
    )

    search_results = [
        {
            "title": "Diabetes",
            "url": "https://example.com",
            "content": (
                "Diabetes affects blood sugar regulation."
            )
        }
    ]

    result = summarize_information(
        {
            "topic": "diabetes",
            "search_results": search_results
        }
    )

    assert result["error"] == ""
    assert result["summary"] == fake_summary

# ---------------------------------------------------------
# Quiz Node Tests
# ---------------------------------------------------------


def test_quiz_without_summary(app):

    generate_quiz = app["generate_quiz"]

    result = generate_quiz(
        {
            "summary": ""
        }
    )

    assert result["quiz_question"] == ""
    assert result["ready_for_quiz"] is False

    assert result["error"] == (
        "Summary is missing. Cannot generate quiz."
    )

def test_quiz_success(app, monkeypatch):

    generate_quiz = app["generate_quiz"]

    fake_question = (
        "What does diabetes affect?"
    )

    monkeypatch.setitem(
        generate_quiz.__globals__,
        "generate_with_gemini",
        lambda prompt: fake_question
    )

    result = generate_quiz(
        {
            "summary": (
                "Diabetes affects blood sugar regulation."
            )
        }
    )

    assert result["error"] == ""
    assert result["ready_for_quiz"] is True
    assert result["quiz_question"] == fake_question

# ---------------------------------------------------------
# Grading Node Tests
# ---------------------------------------------------------


def test_grade_answer_without_answer(app):

    grade_answer = app["grade_answer"]

    result = grade_answer(
        {
            "topic": "diabetes",
            "summary": (
                "Diabetes affects blood sugar regulation."
            ),
            "quiz_question": (
                "What does diabetes affect?"
            ),
            "user_answer": ""
        }
    )

    assert result["grade"] == ""
    assert result["feedback"] == ""

    assert result["error"] == (
        "User answer is missing."
    )

def test_grade_answer_success(app, monkeypatch):

    grade_answer = app["grade_answer"]

    fake_feedback = (
        "Grade: A\n"
        "Explanation: Correct and complete.\n"
        "Evidence: Diabetes affects blood sugar regulation.\n"
        "Source: Test source."
    )

    monkeypatch.setitem(
        grade_answer.__globals__,
        "generate_with_gemini",
        lambda prompt: fake_feedback
    )

    result = grade_answer(
        {
            "topic": "diabetes",
            "summary": (
                "Diabetes affects blood sugar regulation."
            ),
            "quiz_question": (
                "What does diabetes affect?"
            ),
            "user_answer": (
                "It affects blood sugar regulation."
            )
        }
    )

    assert result["error"] == ""
    assert result["grade"] == "A"
    assert result["feedback"] == fake_feedback

def test_grade_answer_invalid_grade(app, monkeypatch):

    grade_answer = app["grade_answer"]

    fake_feedback = (
        "This answer appears reasonable."
    )

    monkeypatch.setitem(
        grade_answer.__globals__,
        "generate_with_gemini",
        lambda prompt: fake_feedback
    )

    result = grade_answer(
        {
            "topic": "diabetes",
            "summary": (
                "Diabetes affects blood sugar regulation."
            ),
            "quiz_question": (
                "What does diabetes affect?"
            ),
            "user_answer": (
                "It affects blood sugar."
            )
        }
    )

    assert result["grade"] == ""

    assert result["error"] == (
        "Gemini returned an invalid grade format."
    )

# ---------------------------------------------------------
# Session Routing Tests
# ---------------------------------------------------------


def test_route_session_continue(app):

    route_session = app["route_session"]

    result = route_session(
        {
            "continue_session": True
        }
    )

    assert result == "reset_state"


def test_route_session_end(app):

    route_session = app["route_session"]
    END = app["END"]

    result = route_session(
        {
            "continue_session": False
        }
    )

    assert result == END

# ---------------------------------------------------------
# Reset Node Tests
# ---------------------------------------------------------


def test_reset_state_node(app):

    reset_state_node = app[
        "reset_state_node"
    ]

    result = reset_state_node(
        {
            "topic": "diabetes",
            "summary": "Some summary",
            "quiz_question": "What is diabetes?",
            "user_answer": "A condition",
            "grade": "A",
            "feedback": "Correct",
            "continue_session": True,
            "error": ""
        }
    )

    assert result["topic"] == ""
    assert result["summary"] == ""
    assert result["quiz_question"] == ""
    assert result["user_answer"] == ""
    assert result["grade"] == ""
    assert result["feedback"] == ""
    assert result["continue_session"] is False
    assert result["error"] == ""