# HealthBot - AI-Powered Patient Education System

## Overview

HealthBot is an AI-powered patient education system built using **Python, LangGraph, LangChain, OpenAI, and Tavily**.

The application helps users learn about health topics and medical conditions by retrieving relevant information from the web, generating a simple patient-friendly summary, and testing the user's understanding through a comprehension quiz.

HealthBot uses **LangGraph** to orchestrate the complete workflow and maintain state between different stages of the application.

> **Medical Disclaimer:** HealthBot is an educational prototype and does not provide medical diagnosis, prescribe medication, or replace advice from a qualified healthcare professional.

## Problem Statement

Patients often have difficulty understanding medical conditions, treatments, symptoms, and general healthcare information because medical information can be complex and difficult to interpret.

HealthBot addresses this problem by providing a simple conversational workflow that:

1. Accepts a health topic from the user.
2. Searches for relevant and current medical information.
3. Converts the information into a patient-friendly explanation.
4. Tests the user's understanding with a comprehension question.
5. Evaluates the user's answer.
6. Provides a grade and explanation.
7. Allows the user to learn about another health topic.

The goal is to demonstrate how Generative AI and workflow orchestration can be used to build an interactive patient education system.

## Objectives

The main objectives of HealthBot are:

- Provide easy-to-understand information about health topics.
- Retrieve current information using web search.
- Use reliable search results as the basis for AI-generated summaries.
- Generate patient-friendly explanations.
- Test user comprehension using a quiz.
- Grade answers based only on the information provided in the summary.
- Provide explanations and supporting references for grades.
- Maintain workflow state using LangGraph.
- Handle invalid user inputs gracefully.
- Handle API failures and unexpected errors.
- Reset the application state when the user starts a new topic.
- Provide a clean exit mechanism.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11.13 | Core programming language |
| Jupyter Notebook | Main application and demonstration |
| LangGraph | Workflow orchestration and state management |
| LangChain | LLM and tool integration |
| OpenAI | Summarization, quiz generation, and answer grading |
| Tavily | Web search and information retrieval |
| python-dotenv | Environment variable management |
| Pytest | Automated testing |

### Why These Technologies?

**LangGraph** is used to represent the HealthBot workflow as a stateful graph consisting of multiple nodes and conditional edges.

**LangChain** provides the integration layer for connecting the application with the LLM and Tavily search tool.

**OpenAI** is responsible for transforming retrieved information into patient-friendly content, generating the comprehension question, and evaluating the user's answer.

**Tavily** provides current web-based information that is passed to the AI model.

**Pytest** is used to test validation, state management, error handling, and workflow behavior.

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

HealthBot follows a stateful workflow implemented using LangGraph.

```text
START
  |
  v
Get Health Topic
  |
  v
Validate Input
  |
  v
Search Medical Information
  |
  v
Generate Patient-Friendly Summary
  |
  v
Display Summary
  |
  v
Ask if User is Ready
  |
  v
Generate One Quiz Question
  |
  v
Get User Answer
  |
  v
Grade Answer
  |
  v
Display Grade and Explanation
  |
  v
Ask for Next Action
  |
  +-------------------+
  |                   |
  | Another Topic     | Exit
  v                   v
Reset State           END
  |
  v
Get Health Topic
```

## LangGraph Architecture

HealthBot is implemented as a stateful LangGraph workflow.

### State

The application state contains information shared between workflow nodes.

Typical state fields include:

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

## Information Retrieval and Summarization

### Tavily Search

HealthBot uses Tavily through the LangChain-compatible search tool to retrieve relevant medical information.

Search queries are constructed using the user's health topic and relevant medical-information keywords.

The application should prioritize reputable sources such as:

- Government health organizations
- Recognized medical institutions
- Hospitals
- Established healthcare organizations
- Reputable medical information providers

### Summarization

The retrieved Tavily information is passed to OpenAI for summarization.

The summarization prompt instructs the model to:

- Use only the provided Tavily results.
- Avoid using outside information.
- Generate a 3–4 paragraph explanation.
- Use simple and patient-friendly language.
- Avoid diagnosing the user.
- Avoid unsupported medical claims.
- Preserve relevant source information.

The summary therefore remains grounded in the information retrieved during the search process.

## Comprehension Quiz

After the user reads the summary, HealthBot generates exactly **one comprehension question**.

The quiz-generation process uses only the generated summary.

The model is instructed to:

- Generate exactly one question.
- Use only information present in the summary.
- Avoid introducing external knowledge.
- Ensure that the question can be answered using the summary.

Example:

```text
Summary:
Regular physical activity can improve cardiovascular health.

Question:
What health benefit of regular physical activity is mentioned in the summary?
```

## Answer Grading

The user's answer is evaluated using the generated summary as the source of truth.

The grading process provides:

- A grade such as A, B, C, or D.
- An explanation of the grade.
- Supporting evidence from the summary.
- Relevant citations or source references.

The grading prompt explicitly instructs the model not to use outside knowledge.

### Example

```text
Grade: B

Explanation:
The answer identifies the main concept correctly but does not
include all of the information described in the summary.

Evidence:
The summary explains that ...

Source:
Relevant source reference
```

## Input Validation

HealthBot validates user input throughout the workflow.

### Health Topic

The application rejects:

- Empty input.
- Whitespace-only input.
- Extremely short or meaningless input.

Example:

```text
Please enter a valid health topic or medical condition.
Accepted inputs: yes/y/ready/no/n
Supported exit commands: exit/quit/q
```

## Error Handling

HealthBot includes error handling at different levels of the application.

### API Configuration Errors

The application checks that required API keys are available before starting.

Missing credentials result in a clear configuration error.

### Tavily Errors

The application handles:

- Invalid API keys.
- Network failures.
- Rate limits.
- Service errors.
- Empty search results.

Limited retries can be used for temporary failures.

If the search ultimately fails, the user receives a clear message rather than a Python traceback.

### OpenAI Errors

The application handles:

- Invalid API keys.
- Rate limits.
- Timeouts.
- Service failures.
- Empty model responses.

Temporary failures can be retried before returning a graceful error.

### Empty Search Results

If Tavily does not return useful information, HealthBot does not invent medical information.

The user is asked to try a more specific health topic.

### Empty Model Responses

If the model returns an empty summary, quiz question, or grading response, the application handles the failure instead of continuing with invalid state.

### Unexpected Errors

Unexpected internal errors should not expose technical details to the user.

Example:

```text
Something went wrong while processing your request.
Please try again.
```

## State Reset

State reset is required when the user chooses to learn about another topic.

For example:

```text
Topic 1: Diabetes
        |
        v
Summary: Diabetes information
        |
        v
Quiz and Grade
        |
        v
New Topic: Hypertension
```

## Medical Safety

HealthBot is designed as a patient education prototype and not as a medical diagnostic system.

The AI prompts instruct the model to:

- Provide general educational information.
- Avoid diagnosing individual users.
- Avoid prescribing medication.
- Avoid recommending changes to prescribed treatment.
- Avoid unsupported medical claims.
- Encourage consultation with qualified healthcare professionals when appropriate.

A disclaimer is displayed to make the purpose of the system clear:

```text
This information is for educational purposes only and does not replace
advice from a qualified healthcare professional.
```

## Testing

HealthBot uses **Pytest** for automated testing.

Tests are located in:

```text
tests/
└── test_healthbot.py
```

## Test Cases

| Test Case | Expected Result |
|---|---|
| Valid health topic | Workflow continues |
| Empty topic | User is asked again |
| Whitespace topic | User is asked again |
| Very short topic | User is asked for a better topic |
| No useful search results | Graceful error |
| Tavily failure | Retry and/or graceful error |
| OpenAI failure | Retry and/or graceful error |
| Empty summary | Graceful failure |
| Valid ready response | Continue |
| Invalid ready response | Ask again |
| Quiz generated | Exactly one question |
| Empty quiz answer | Ask again |
| Valid quiz answer | Answer is graded |
| Answer grading | Grade and explanation returned |
| New topic | Previous state is cleared |
| Exit command | Workflow terminates |

## Installation

### 1. Clone or download the project

```bash
cd healthbot
```

### 2. Create the virtual environment

```bash
pip install uv
uv venv --python 3.11.13
```

### 3. Activate the environment

#### Windows PowerShell:
```bash
.\\.venv\\Scripts\\Activate
```
#### macOS/Linux:
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
uv add -r requirements.txt
```

### 5. Configure API keys
```bash
OPENAI_API_KEY="your-openai-api-key"
TAVILY_API_KEY="your-tavily-api-key"
```

### 6. Run the application
```bash
healthbot.ipynb
```

### 7. Run tests
```bash
pytest -v
```

## Example Usage

A typical session looks like:

```text
==================================================
HEALTHBOT
AI-Powered Patient Education System
==================================================

What health topic would you like to learn about?

> diabetes

Searching reliable medical sources...

==================================================
HEALTH INFORMATION
==================================================

[3–4 paragraph patient-friendly summary]

==================================================

Are you ready for the comprehension check?

> ready

==================================================
COMPREHENSION CHECK
==================================================

[One comprehension question]

Your answer:
> [user answer]

==================================================
RESULT
==================================================

Grade: A

Explanation:
[Explanation based on the summary]

Evidence:
[Relevant information from the summary]

Sources:
[Relevant source references]

Would you like to learn about another health topic?

> no

Thank you for using HealthBot.
```

## Conclusion


HealthBot demonstrates how Generative AI, web search, tool calling, state management, and LangGraph workflow orchestration can be combined to create an interactive patient education application.

The system retrieves current information, produces grounded patient-friendly explanations, tests comprehension, evaluates answers, handles invalid inputs and API failures, and maintains clean state between topics.

The project provides a practical demonstration of Full Stack Generative AI concepts while keeping the implementation simple enough to understand, test, and demonstrate.