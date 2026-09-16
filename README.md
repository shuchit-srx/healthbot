# HealthBot

HealthBot is an AI-powered patient education application that validates health topics, retrieves medical information from web sources, generates patient-friendly explanations using Gemini, creates comprehension quizzes, evaluates answers, and supports continued learning sessions.

## Architecture

```text
Next.js Frontend
       |
       | REST / NDJSON
       v
FastAPI Backend
       |
       +---- Topic Validation
       |
       +---- Tavily Medical Search
       |
       +---- Gemini AI
       |
       +---- LangGraph Workflow
       |
       +---- Quiz Generation
       |
       +---- Answer Grading
       |
       v
Structured Response