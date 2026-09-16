const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";


export class ApiError extends Error {
  status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
  }
}


async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  try {
    const response = await fetch(
      `${API_URL}${endpoint}`,
      {
        ...options,

        headers: {
          "Content-Type": "application/json",
          ...(options?.headers || {}),
        },
      },
    );

    let data: unknown;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      let message =
        "Something went wrong. Please try again.";

      if (
        data &&
        typeof data === "object" &&
        "detail" in data
      ) {
        const detail = (
          data as {
            detail?: unknown;
          }
        ).detail;

        if (typeof detail === "string") {
          message = detail;
        }
      }

      throw new ApiError(
        message,
        response.status,
      );
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      "Unable to connect to HealthBot. Please check that the backend is running.",
      0,
    );
  }
}


export interface TopicValidationResponse {
  valid: boolean;
  topic?: string;
  message?: string;
}


export interface SummaryResponse {
  topic: string;
  summary: string;
}


export interface QuizResponse {
  question: string;
}


export interface GradeResponse {
  grade: string;
  feedback: string;
}


export async function validateTopic(
  topic: string,
): Promise<TopicValidationResponse> {
  return request<TopicValidationResponse>(
    "/api/topics/validate",
    {
      method: "POST",

      body: JSON.stringify({
        topic: topic.trim(),
      }),
    },
  );
}


export async function generateSummary(
  topic: string,
): Promise<SummaryResponse> {
  return request<SummaryResponse>(
    "/api/education/summary",
    {
      method: "POST",

      body: JSON.stringify({
        topic: topic.trim(),
      }),
    },
  );
}


export async function generateQuiz(
  summary: string,
): Promise<QuizResponse> {
  return request<QuizResponse>(
    `/api/quiz/generate?summary=${encodeURIComponent(
      summary,
    )}`,
    {
      method: "POST",
    },
  );
}


export async function gradeQuiz(
  topic: string,
  summary: string,
  question: string,
  answer: string,
): Promise<GradeResponse> {
  const params = new URLSearchParams({
    topic,
    summary,
    question,
    answer,
  });

  return request<GradeResponse>(
    `/api/quiz/grade?${params.toString()}`,
    {
      method: "POST",
    },
  );
}