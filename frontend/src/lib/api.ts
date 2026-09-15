import type {
  TopicValidationResponse,
  SummaryResponse,
  QuizResponse,
  GradeResponse,
  SessionResponse,
} from "@/src/types/healthbot";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

async function handleResponse<T>(
  response: Response
): Promise<T> {
  if (!response.ok) {
    let message = "Something went wrong.";

    try {
      const data = await response.json();

      if (data?.detail) {
        message =
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Ignore invalid error responses.
    }

    throw new Error(message);
  }

  return response.json();
}

/**
 * Validate a health topic.
 */
export async function validateTopic(
  topic: string
): Promise<TopicValidationResponse> {
  const response = await fetch(
    `${API_URL}/api/topics/validate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        topic,
      }),
    }
  );

  return handleResponse<TopicValidationResponse>(
    response
  );
}

/**
 * Generate a patient-friendly health summary.
 */
export async function generateSummary(
  topic: string
): Promise<SummaryResponse> {
  const response = await fetch(
    `${API_URL}/api/education/summary`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        topic,
      }),
    }
  );

  return handleResponse<SummaryResponse>(
    response
  );
}

/**
 * Generate a comprehension quiz from the summary.
 */
export async function generateQuiz(
  summary: string
): Promise<QuizResponse> {
  const params = new URLSearchParams({
    summary,
  });

  const response = await fetch(
    `${API_URL}/api/quiz/generate?${params.toString()}`,
    {
      method: "POST",
    }
  );

  return handleResponse<QuizResponse>(
    response
  );
}

/**
 * Grade the user's quiz answer.
 */
export async function gradeAnswer(
  topic: string,
  summary: string,
  quizQuestion: string,
  userAnswer: string
): Promise<GradeResponse> {
  const params = new URLSearchParams({
    topic,
    summary,
    quiz_question: quizQuestion,
  });

  const response = await fetch(
    `${API_URL}/api/quiz/grade?${params.toString()}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_answer: userAnswer,
      }),
    }
  );

  return handleResponse<GradeResponse>(
    response
  );
}

/**
 * Decide whether to continue or finish the session.
 */
export async function decideSession(
  continueSession: boolean
): Promise<SessionResponse> {
  const response = await fetch(
    `${API_URL}/api/session/decision`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        continue_session: continueSession,
      }),
    }
  );

  return handleResponse<SessionResponse>(
    response
  );
}