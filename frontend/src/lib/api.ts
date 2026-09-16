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

    let data: unknown = null;

    try {
      data = await response.json();
    } catch {}

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
  sources?: unknown[];
}

export interface QuizResponse {
  question: string;
}

export interface GradeResponse {
  grade: string;
  feedback: string;
}

export interface SessionResponse {
  continue_session: boolean;
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

export async function streamSummary(
  topic: string,
  onChunk: (
    chunk: string,
  ) => void,
  signal?: AbortSignal,
): Promise<void> {
  let response: Response;

  try {
    response = await fetch(
      `${API_URL}/api/education/summary/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
        }),
        signal,
      },
    );
  } catch (error) {
    if (
      error instanceof DOMException &&
      error.name === "AbortError"
    ) {
      throw error;
    }

    throw new ApiError(
      "Unable to connect to HealthBot. Please check that the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(
      "Unable to generate the health summary.",
      response.status,
    );
  }

  if (!response.body) {
    throw new ApiError(
      "The server did not provide a streaming response.",
      0,
    );
  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  let buffer = "";

  try {
    while (true) {
      const {
        value,
        done,
      } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true,
        },
      );

      const lines =
        buffer.split("\n");

      buffer =
        lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) {
          continue;
        }

        const event =
          JSON.parse(line);

        if (
          event.type === "chunk" &&
          typeof event.content === "string"
        ) {
          onChunk(
            event.content,
          );
        }

        if (
          event.type === "error"
        ) {
          throw new ApiError(
            event.message ||
              "Unable to complete the response. Please try again.",
            500,
          );
        }

        if (
          event.type === "done"
        ) {
          return;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
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
  const params =
    new URLSearchParams({
      topic,
      summary,
      quiz_question:
        question,
    });

  return request<GradeResponse>(
    `/api/quiz/grade?${params.toString()}`,
    {
      method: "POST",
      body: JSON.stringify({
        user_answer: answer,
      }),
    },
  );
}

export async function decideSession(
  continueSession: boolean,
): Promise<SessionResponse> {
  return request<{
    data: SessionResponse;
  }>(
    "/api/session/decision",
    {
      method: "POST",
      body: JSON.stringify({
        continue_session:
          continueSession,
      }),
    },
  ).then(
    (response) => response.data,
  );
}