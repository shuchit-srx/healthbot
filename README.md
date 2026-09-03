# HealthBot - AI-Powered Patient Education System

## Overview

HealthBot is an AI-powered patient education system built using **Python, LangGraph, LangChain, Google Gemini, and Tavily**.

It helps users learn about health topics by retrieving medical information from the web, generating a patient-friendly summary, and testing understanding through a short comprehension quiz.

> **Medical Disclaimer:** HealthBot is an educational prototype. It does not diagnose medical conditions, prescribe medication, or replace professional medical advice.

## Problem Statement

Medical information can be complex and difficult for patients to understand.

HealthBot simplifies this process by:

- Accepting a health topic from the user.
- Validating and correcting the topic.
- Retrieving relevant medical information using Tavily.
- Generating a patient-friendly summary using Gemini.
- Generating one comprehension question.
- Grading the user's answer using the summary as the source of truth.
- Allowing the user to continue with another topic.

## Key Features

- Health-topic validation using **exact matching, fuzzy matching, and Gemini classification**.
- Spelling correction for common health-topic variations.
- Web-based medical information retrieval using **Tavily**.
- Grounded patient-friendly summaries using **Google Gemini**.
- One-question comprehension check.
- A–D answer grading with explanation and evidence.
- Stateful workflow orchestration using **LangGraph**.
- Retry handling for temporary API failures.
- Graceful handling of invalid input and unexpected responses.
- Automated testing using **Pytest**.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11.13 | Core programming language |
| Jupyter Notebook | Application and demonstration |
| LangGraph | Workflow orchestration and state management |
| LangChain | AI and tool integration |
| Google Gemini | Classification, summarization, quiz generation, and grading |
| Tavily | Medical web search |
| RapidFuzz | Health-topic matching and spelling correction |
| Pytest | Automated testing |
| python-dotenv | Environment configuration |

## Project Structure

```text
healthbot/
│
├── healthbot.ipynb
├── config.env
├── requirements.txt
├── README.md
├── .gitignore
│
└── tests/
    └── test_healthbot.py
```

## Application Workflow

HealthBot is implemented as a stateful LangGraph workflow.

```text
START
  |
  v
Get Health Topic
  |
  v
Validate Topic
  |
  v
Search Medical Information
  |
  v
Generate Summary
  |
  v
Display Summary
  |
  v
Ready for Quiz?
  |------------------|
 Yes                 No
  |                   |
  v                   v
Generate Quiz    Session Decision
  |
  v
Get Answer
  |
  v
Grade Answer
  |
  v
Display Feedback
  |
  v
Session Decision
  |------------------|
Another Topic       Exit
  |                   |
  v                   v
Reset State          END
  |
  v
Get Health Topic
```

## Quick Demonstration

The notebook includes a **Quick Demonstration** section that showcases the core workflow using a sample health topic.

It demonstrates:

- Health-topic validation
- Tavily medical search
- Gemini-generated summary
- Comprehension question generation
- Answer grading
- LangGraph state updates
- Complete workflow structure and routing

The final application cell provides the interactive end-to-end HealthBot experience.

## LangGraph State

The workflow maintains shared state using a "TypedDict":

```text
topic
search_results
summary
quiz_question
user_answer
grade
feedback
ready_for_quiz
continue_session
error
```

## AI Workflow

### Topic Validation

The user's topic passes through:

```text
Normalize
   ↓
Exact Match
   ↓
Fuzzy Match
   ↓
Gemini Classification
```
This allows HealthBot to handle common spelling mistakes while rejecting non-health-related topics.

### Information Retrieval

Tavily searches the web using the validated health topic and medical-information keywords.

Only search results containing usable content are passed to Gemini.

### Patient-Friendly Summary

Gemini generates a 3–4 paragraph explanation using only the retrieved search results.

The prompt instructs the model to avoid:

- Diagnosis
- Personalized medical advice
- Medication prescriptions
- Unsupported medical claims

### Comprehension Quiz

If the user chooses Yes, Gemini generates exactly one question based only on the generated summary.

If the user chooses No, the quiz is skipped.

### Answer Grading

The user's answer is evaluated against the generated summary.

The result contains:

```text
Grade: A / B / C / D
Explanation
Evidence
Source
```

## Error Handling

HealthBot handles failures at multiple stages:

- Missing API credentials.
- Invalid or empty user input.
- Tavily search failures.
- Empty search results.
- Gemini service failures.
- Empty or malformed Gemini responses.
- Invalid grading output.
- Temporary failures using retry logic.

Errors are stored in the workflow state and handled without unnecessarily terminating the application.

## Testing

Automated tests are implemented using Pytest.

```bash
pytest -v
```

The test suite covers:

- Utility functions
- Prompt formatting
- Retry behavior
- Health-topic validation
- Gemini response handling
- Workflow nodes
- Error handling
- Quiz routing
- Session routing
- State reset
- End-to-end workflow behavior with mocked external services

## Installation

### Create Environment

```bash
pip install uv
uv venv --python 3.11.13
```

### Activate Environment

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate
```

### Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Show the Dependencies

```bash
pip list
```

### Configure API Keys

Create `config.env` in the project root:

```env
GEMINI_API_KEY="your-gemini-api-key"
TAVILY_API_KEY="your-tavily-api-key"
```
`config.env` is excluded from Git using `.gitignore.`

### Run the Application

Open `healthbot.ipynb` and run the notebook cells in order.

The **Quick Demonstration** section provides a non-interactive demonstration of the core workflow, while the final application cell runs the complete interactive HealthBot experience.

#### Example

```text
What health topic or medical condition would you like to learn about?
> diabetes

HEALTH INFORMATION

[Patient-friendly summary]

Are you ready for the comprehension check? (yes/no)
> yes

Question:
[Generated question]

Your answer:
> [User answer]

QUIZ RESULT

Grade: A

Feedback:
[Explanation and evidence]

Would you like to learn about another health topic? (yes/no)
> no
```

## Limitations

- HealthBot is an educational prototype, not a diagnostic system.
- Generated information depends on the quality of retrieved web sources and AI responses.
- The system depends on external Gemini and Tavily APIs.
- The current implementation runs as a Jupyter Notebook rather than a production web application.

## Conclusion

Conclusion

HealthBot demonstrates how **Generative AI, web search, LangChain, and LangGraph** can be combined to build a stateful patient education workflow.

The project focuses on **grounded information retrieval, patient-friendly generation, comprehension evaluation, error handling, and workflow orchestration** while keeping the implementation simple and testable.