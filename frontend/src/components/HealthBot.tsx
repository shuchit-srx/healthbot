"use client";

import {
  AlertCircle,
  CheckCircle2,
  FileText,
  HeartPulse,
  Loader2,
  RotateCcw,
  Sparkles,
  XCircle,
} from "lucide-react";
import { useRef, useState } from "react";

import {
  decideSession,
  generateQuiz,
  gradeQuiz,
  streamSummary,
  validateTopic,
} from "@/src/lib/api";

import Footer from "./Footer";
import Header from "./Header";
import TopicInput from "./TopicInput";

const SUGGESTIONS = [
  "Diabetes",
  "High blood pressure",
  "Sleep health",
  "Vitamin D",
  "Heart health",
];

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type QuizState = {
  question: string;
  answer: string;
  grade: string | null;
  feedback: string | null;
};

export default function HealthBot() {
  const [topic, setTopic] =
    useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [quiz, setQuiz] =
    useState<QuizState | null>(null);

  const [quizLoading, setQuizLoading] =
    useState(false);

  const [gradeLoading, setGradeLoading] =
    useState(false);

  const [sessionActive, setSessionActive] =
    useState(false);

  const abortControllerRef =
    useRef<AbortController | null>(null);

  function createId() {
    if (
      typeof crypto !== "undefined" &&
      crypto.randomUUID
    ) {
      return crypto.randomUUID();
    }

    return `${Date.now()}-${Math.random()}`;
  }

  function resetConversation() {
    abortControllerRef.current?.abort();

    setMessages([]);
    setTopic("");
    setError(null);
    setQuiz(null);
    setSessionActive(false);
    setLoading(false);
    setQuizLoading(false);
    setGradeLoading(false);
  }

  async function askTopic(
    requestedTopic?: string,
  ) {
    const selectedTopic =
      (requestedTopic ?? topic).trim();

    if (!selectedTopic || loading) {
      return;
    }

    if (selectedTopic.length > 200) {
      setError(
        "Please keep the health topic under 200 characters.",
      );
      return;
    }

    setError(null);
    setQuiz(null);
    setSessionActive(true);
    setLoading(true);

    setMessages((current) => [
      ...current,
      {
        id: createId(),
        role: "user",
        content: selectedTopic,
      },
    ]);

    setTopic("");

    try {
      const validation =
        await validateTopic(
          selectedTopic,
        );

      if (!validation.valid) {
        throw new Error(
          validation.message ||
            "Please enter a valid health topic.",
        );
      }

      const assistantId = createId();

      setMessages((current) => [
        ...current,
        {
          id: assistantId,
          role: "assistant",
          content: "",
        },
      ]);

      const controller =
        new AbortController();

      abortControllerRef.current =
        controller;

      await streamSummary(
        selectedTopic,
        (chunk) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content:
                      message.content +
                      chunk,
                  }
                : message,
            ),
          );
        },
        controller.signal,
      );
    } catch (err) {
      if (
        err instanceof DOMException &&
        err.name === "AbortError"
      ) {
        return;
      }

      const message =
        err instanceof Error
          ? err.message
          : "Unable to complete the request.";

      setError(message);

      setMessages((current) =>
        current.filter(
          (message) =>
            message.content.length > 0 ||
            message.role === "user",
        ),
      );
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }

  async function handleGenerateQuiz() {
    const assistantMessages =
      messages.filter(
        (message) =>
          message.role === "assistant" &&
          message.content.trim(),
      );

    const latestSummary =
      assistantMessages[
        assistantMessages.length - 1
      ]?.content;

    if (!latestSummary || quizLoading) {
      return;
    }

    setQuizLoading(true);
    setError(null);

    try {
      const result =
        await generateQuiz(
          latestSummary,
        );

      setQuiz({
        question: result.question,
        answer: "",
        grade: null,
        feedback: null,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate the quiz.",
      );
    } finally {
      setQuizLoading(false);
    }
  }

  async function handleGradeQuiz() {
    if (
      !quiz ||
      !quiz.answer.trim() ||
      gradeLoading
    ) {
      return;
    }

    const userMessages =
      messages.filter(
        (message) =>
          message.role === "user",
      );

    const latestTopic =
      userMessages[
        userMessages.length - 1
      ]?.content;

    const assistantMessages =
      messages.filter(
        (message) =>
          message.role === "assistant",
      );

    const latestSummary =
      assistantMessages[
        assistantMessages.length - 1
      ]?.content;

    if (
      !latestTopic ||
      !latestSummary
    ) {
      return;
    }

    setGradeLoading(true);
    setError(null);

    try {
      const result =
        await gradeQuiz(
          latestTopic,
          latestSummary,
          quiz.question,
          quiz.answer,
        );

      setQuiz((current) =>
        current
          ? {
              ...current,
              grade: result.grade,
              feedback: result.feedback,
            }
          : null,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to grade the answer.",
      );
    } finally {
      setGradeLoading(false);
    }
  }

  async function handleContinue(
    continueSession: boolean,
  ) {
    try {
      const result =
        await decideSession(
          continueSession,
        );

      setSessionActive(
        result.continue_session,
      );

      if (!result.continue_session) {
        setQuiz(null);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update the session.",
      );
    }
  }

  const hasConversation =
    messages.length > 0;

  const hasSummary =
    messages.some(
      (message) =>
        message.role === "assistant" &&
        message.content.trim(),
    );

  const latestAssistant =
    [...messages]
      .reverse()
      .find(
        (message) =>
          message.role === "assistant",
      );

  return (
    <div className="app-shell">
      <Header />

      <main className="app-main">
        {!hasConversation ? (
          <section className="home-page">
            <div className="home-content">
              <div className="hero">
                <div
                  className="hero-orb"
                  aria-hidden="true"
                />

                <h1>
                  Hello, how can I help?
                </h1>

                <p>
                  Ask HealthBot about a health
                  topic and get clear,
                  evidence-informed educational
                  information powered by AI.
                </p>
              </div>

              <TopicInput
                value={topic}
                onChange={setTopic}
                onSubmit={() =>
                  askTopic()
                }
                disabled={loading}
              />

              <div className="suggestions">
                {SUGGESTIONS.map(
                  (suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="suggestion-chip"
                      onClick={() =>
                        askTopic(
                          suggestion,
                        )
                      }
                      disabled={loading}
                    >
                      <Sparkles size={14} />
                      {suggestion}
                    </button>
                  ),
                )}
              </div>

              {error && (
                <ErrorMessage
                  error={error}
                  onRetry={() =>
                    askTopic()
                  }
                />
              )}
            </div>

            <Footer />
          </section>
        ) : (
          <section className="chat-page">
            <div className="chat-list">
              {messages.map(
                (message) => {
                  if (
                    message.role === "user"
                  ) {
                    return (
                      <div
                        className="message-row user"
                        key={message.id}
                      >
                        <div className="user-message">
                          {message.content}
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      className="message-row assistant"
                      key={message.id}
                    >
                      <div className="assistant-message">
                        <div className="assistant-avatar">
                          <HeartPulse
                            size={18}
                          />
                        </div>

                        <div className="assistant-content">
                          <div className="assistant-name">
                            HealthBot
                          </div>

                          {message.content ? (
                            <div className="summary-content">
                              {message.content}
                            </div>
                          ) : (
                            <LoadingDots />
                          )}
                        </div>
                      </div>
                    </div>
                  );
                },
              )}

              {error && (
                <ErrorMessage
                  error={error}
                  onRetry={() =>
                    askTopic()
                  }
                />
              )}

              {hasSummary &&
                latestAssistant?.content && (
                  <>
                    <div className="quiz-actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={
                          handleGenerateQuiz
                        }
                        disabled={
                          quizLoading ||
                          loading
                        }
                      >
                        {quizLoading ? (
                          <>
                            <Loader2
                              size={17}
                              className="spin"
                            />
                            Creating quiz...
                          </>
                        ) : (
                          <>
                            <FileText
                              size={17}
                            />
                            Test my knowledge
                          </>
                        )}
                      </button>
                    </div>

                    {quiz && (
                      <QuizCard
                        quiz={quiz}
                        setQuiz={setQuiz}
                        loading={
                          gradeLoading
                        }
                        onGrade={
                          handleGradeQuiz
                        }
                      />
                    )}

                    {quiz?.grade &&
                      quiz.feedback && (
                        <GradeResult
                          grade={quiz.grade}
                          feedback={
                            quiz.feedback
                          }
                        />
                      )}

                    {quiz?.grade && (
                      <div className="quiz-actions">
                        <button
                          type="button"
                          className="suggestion-chip"
                          onClick={() =>
                            handleContinue(
                              true,
                            )
                          }
                        >
                          Continue learning
                        </button>

                        <button
                          type="button"
                          className="suggestion-chip"
                          onClick={() =>
                            handleContinue(
                              false,
                            )
                          }
                        >
                          End session
                        </button>
                      </div>
                    )}
                  </>
                )}
            </div>

            {sessionActive && (
              <div className="composer">
                <div className="composer-inner">
                  <TopicInput
                    value={topic}
                    onChange={setTopic}
                    onSubmit={() =>
                      askTopic()
                    }
                    disabled={loading}
                    placeholder="Ask a follow-up..."
                  />
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      {hasConversation && (
        <div
          style={{
            position: "fixed",
            left: 20,
            bottom: 20,
            zIndex: 45,
          }}
        >
          <button
            type="button"
            className="icon-button"
            onClick={
              resetConversation
            }
            title="New conversation"
            aria-label="Start new conversation"
          >
            <RotateCcw size={18} />
          </button>
        </div>
      )}
    </div>
  );
}

function LoadingDots() {
  return (
    <div
      className="loading-dots"
      aria-label="HealthBot is thinking"
    >
      <span className="loading-dot" />
      <span className="loading-dot" />
      <span className="loading-dot" />
    </div>
  );
}

function ErrorMessage({
  error,
  onRetry,
}: {
  error: string;
  onRetry: () => void;
}) {
  return (
    <div className="error-card">
      <div className="error-content">
        <AlertCircle
          size={18}
          style={{ flexShrink: 0 }}
        />

        <span>{error}</span>
      </div>

      <button
        type="button"
        className="retry-button"
        onClick={onRetry}
      >
        Try again
      </button>
    </div>
  );
}

function QuizCard({
  quiz,
  setQuiz,
  loading,
  onGrade,
}: {
  quiz: QuizState;
  setQuiz: React.Dispatch<
    React.SetStateAction<QuizState | null>
  >;
  loading: boolean;
  onGrade: () => void;
}) {
  return (
    <div className="quiz-card">
      <div className="quiz-label">
        <Sparkles size={15} />
        Knowledge check
      </div>

      <div className="quiz-question">
        {quiz.question}
      </div>

      <textarea
        className="answer-input"
        value={quiz.answer}
        onChange={(event) =>
          setQuiz((current) =>
            current
              ? {
                  ...current,
                  answer:
                    event.target.value.slice(
                      0,
                      2000,
                    ),
                }
              : null,
          )
        }
        maxLength={2000}
        placeholder="Write your answer..."
        disabled={loading}
      />

      <div className="quiz-actions">
        <button
          type="button"
          className="primary-button"
          onClick={onGrade}
          disabled={
            loading ||
            !quiz.answer.trim()
          }
        >
          {loading ? (
            <>
              <Loader2
                size={17}
                className="spin"
              />
              Checking...
            </>
          ) : (
            "Submit answer"
          )}
        </button>
      </div>
    </div>
  );
}

function GradeResult({
  grade,
  feedback,
}: {
  grade: string;
  feedback: string;
}) {
  const normalized =
    grade.toLowerCase();

  const correct =
    normalized.includes("correct") ||
    normalized.includes("excellent") ||
    normalized.includes("good");

  return (
    <div
      className={`grade-card ${
        correct
          ? "correct"
          : "incorrect"
      }`}
    >
      <div className="grade-heading">
        {correct ? (
          <CheckCircle2 size={19} />
        ) : (
          <XCircle size={19} />
        )}

        {grade}
      </div>

      <div className="grade-feedback">
        {feedback}
      </div>
    </div>
  );
}