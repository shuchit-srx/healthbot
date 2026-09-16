"use client";

import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  ApiError,
  decideSession,
  generateQuiz,
  gradeQuiz,
  streamSummary,
  validateTopic,
} from "@/src/lib/api";

type MessageRole =
  | "user"
  | "assistant";

type MessageType =
  | "normal"
  | "summary"
  | "quiz"
  | "feedback";

type Message = {
  id: string;
  role: MessageRole;
  content: string;
  type: MessageType;
};

type LoadingStage =
  | "idle"
  | "validating"
  | "researching"
  | "generating"
  | "quiz"
  | "grading";

const MAX_TOPIC_LENGTH = 200;
const MAX_ANSWER_LENGTH = 2000;

export default function HealthBot() {
  const [messages, setMessages] =
    useState<Message[]>([]);

  const [input, setInput] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [loadingStage, setLoadingStage] =
    useState<LoadingStage>("idle");

  const [error, setError] =
    useState<string | null>(null);

  const [currentTopic, setCurrentTopic] =
    useState("");

  const [currentSummary, setCurrentSummary] =
    useState("");

  const [currentQuestion, setCurrentQuestion] =
    useState("");

  const abortControllerRef =
    useRef<AbortController | null>(null);

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  const isLoading =
    loadingStage !== "idle";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const addMessage = (
    role: MessageRole,
    content: string,
    type: MessageType = "normal",
  ) => {
    const id = crypto.randomUUID();

    setMessages((previous) => [
      ...previous,
      {
        id,
        role,
        content,
        type,
      },
    ]);

    return id;
  };

  const updateMessage = (
    id: string,
    content: string,
  ) => {
    setMessages((previous) =>
      previous.map((message) =>
        message.id === id
          ? {
              ...message,
              content,
            }
          : message,
      ),
    );
  };

  const removeMessage = (
    id: string,
  ) => {
    setMessages((previous) =>
      previous.filter(
        (message) =>
          message.id !== id,
      ),
    );
  };

  const handleError = (
    err: unknown,
  ) => {
    if (
      err instanceof DOMException &&
      err.name === "AbortError"
    ) {
      return;
    }

    if (err instanceof ApiError) {
      setError(err.message);
      return;
    }

    if (err instanceof Error) {
      setError(err.message);
      return;
    }

    setError(
      "Something went wrong. Please try again.",
    );
  };

  const handleSubmit = async (
    event: FormEvent,
  ) => {
    event.preventDefault();

    if (isLoading) {
      return;
    }

    const topic =
      input.trim();

    if (!topic) {
      setError(
        "Please enter a health topic.",
      );
      return;
    }

    if (
      topic.length >
      MAX_TOPIC_LENGTH
    ) {
      setError(
        "Please keep the health topic under 200 characters.",
      );
      return;
    }

    setError(null);
    setInput("");
    setCurrentTopic(topic);
    setCurrentSummary("");
    setCurrentQuestion("");
    setAnswer("");

    addMessage(
      "user",
      topic,
    );

    await processTopic(topic);
  };

  const processTopic = async (
    topic: string,
  ) => {
    abortControllerRef.current?.abort();

    const controller =
      new AbortController();

    abortControllerRef.current =
      controller;

    try {
      setLoadingStage(
        "validating",
      );

      const validation =
        await validateTopic(
          topic,
        );

      if (!validation.valid) {
        setError(
          validation.message ||
            "Please enter a valid health topic.",
        );

        return;
      }

      setLoadingStage(
        "researching",
      );

      const assistantMessageId =
        addMessage(
          "assistant",
          "",
          "summary",
        );

      setLoadingStage(
        "generating",
      );

      let summary = "";

      await streamSummary(
        validation.topic ||
          topic,
        (chunk) => {
          summary += chunk;

          updateMessage(
            assistantMessageId,
            summary,
          );

          setCurrentSummary(
            summary,
          );
        },
        controller.signal,
      );

      if (!summary.trim()) {
        removeMessage(
          assistantMessageId,
        );

        throw new ApiError(
          "HealthBot returned an empty response. Please try again.",
          500,
        );
      }

      setLoadingStage(
        "quiz",
      );

      const quiz =
        await generateQuiz(
          summary,
        );

      setCurrentQuestion(
        quiz.question,
      );

      addMessage(
        "assistant",
        quiz.question,
        "quiz",
      );
    } catch (err) {
      handleError(err);
    } finally {
      setLoadingStage(
        "idle",
      );

      abortControllerRef.current =
        null;
    }
  };

  const handleGrade = async () => {
    if (
      isLoading ||
      !answer.trim() ||
      !currentSummary ||
      !currentQuestion ||
      !currentTopic
    ) {
      return;
    }

    const userAnswer =
      answer.trim();

    if (
      userAnswer.length >
      MAX_ANSWER_LENGTH
    ) {
      setError(
        "Please keep your answer under 2000 characters.",
      );
      return;
    }

    setError(null);

    addMessage(
      "user",
      userAnswer,
    );

    setAnswer("");

    try {
      setLoadingStage(
        "grading",
      );

      const result =
        await gradeQuiz(
          currentTopic,
          currentSummary,
          currentQuestion,
          userAnswer,
        );

      addMessage(
        "assistant",
        `${result.grade}\n\n${result.feedback}`,
        "feedback",
      );
    } catch (err) {
      handleError(err);
    } finally {
      setLoadingStage(
        "idle",
      );
    }
  };

  const handleContinue =
    async (
      continueSession: boolean,
    ) => {
      if (isLoading) {
        return;
      }

      setError(null);

      try {
        await decideSession(
          continueSession,
        );

        if (continueSession) {
          setCurrentQuestion("");
          setCurrentSummary("");
          setAnswer("");

          addMessage(
            "assistant",
            "Sure. Enter another health topic to continue.",
          );
        } else {
          addMessage(
            "assistant",
            "Session ended. Take care.",
          );
        }
      } catch (err) {
        handleError(err);
      }
    };

  const handleRetry = () => {
    if (
      isLoading ||
      !currentTopic
    ) {
      return;
    }

    setError(null);
    processTopic(
      currentTopic,
    );
  };

  const loadingText = {
    validating:
      "Checking your topic...",
    researching:
      "Researching medical information...",
    generating:
      "Generating your explanation...",
    quiz:
      "Preparing a question...",
    grading:
      "Checking your answer...",
    idle: "",
  }[loadingStage];

  return (
    <div className="flex min-h-[70vh] flex-col">
      <div className="flex-1 space-y-4">
        {messages.map(
          (message) => (
            <div
              key={message.id}
              className={
                message.role ===
                "user"
                  ? "ml-auto max-w-2xl rounded-2xl bg-blue-600 p-4 text-white"
                  : "mr-auto max-w-3xl rounded-2xl border p-4"
              }
            >
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          ),
        )}

        {loadingText && (
          <div
            role="status"
            aria-live="polite"
            className="mr-auto rounded-2xl border p-4"
          >
            {loadingText}
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-300 p-4"
          >
            <p className="text-sm text-red-600">
              {error}
            </p>

            <button
              type="button"
              onClick={
                handleRetry
              }
              disabled={
                isLoading ||
                !currentTopic
              }
              className="mt-3 rounded-lg border px-4 py-2 text-sm"
            >
              Try again
            </button>
          </div>
        )}

        {currentQuestion &&
          !isLoading && (
            <div className="space-y-3">
              <textarea
                value={answer}
                onChange={(event) =>
                  setAnswer(
                    event.target.value,
                  )
                }
                maxLength={
                  MAX_ANSWER_LENGTH
                }
                placeholder="Write your answer..."
                aria-label="Quiz answer"
                className="min-h-28 w-full rounded-xl border p-3"
              />

              <button
                type="button"
                onClick={
                  handleGrade
                }
                disabled={
                  !answer.trim()
                }
                className="rounded-xl border px-5 py-2"
              >
                Submit answer
              </button>
            </div>
          )}

        {!currentQuestion &&
          currentSummary &&
          !isLoading && (
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() =>
                  handleContinue(
                    true,
                  )
                }
                className="rounded-xl border px-5 py-2"
              >
                Continue
              </button>

              <button
                type="button"
                onClick={() =>
                  handleContinue(
                    false,
                  )
                }
                className="rounded-xl border px-5 py-2"
              >
                End session
              </button>
            </div>
          )}

        <div
          ref={messagesEndRef}
        />
      </div>

      <form
        onSubmit={
          handleSubmit
        }
        className="mt-6 flex gap-3"
      >
        <textarea
          value={input}
          onChange={(event) =>
            setInput(
              event.target.value,
            )
          }
          maxLength={
            MAX_TOPIC_LENGTH
          }
          disabled={isLoading}
          placeholder="Ask about a health topic..."
          aria-label="Health topic"
          className="min-h-14 flex-1 rounded-xl border p-3"
        />

        <button
          type="submit"
          disabled={
            isLoading ||
            !input.trim()
          }
          className="rounded-xl border px-5 py-2"
        >
          Ask
        </button>
      </form>
    </div>
  );
}