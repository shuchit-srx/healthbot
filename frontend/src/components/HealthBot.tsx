"use client";

import {
  useState,
} from "react";

import Header from "./Header";
import Footer from "./Footer";
import TopicInput from "./TopicInput";

import {
  ApiError,
  generateQuiz,
  generateSummary,
  validateTopic,
} from "@/src/lib/api";


interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}


export default function HealthBot() {
  const [messages, setMessages] =
    useState<Message[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const addMessage = (
    role: Message["role"],
    content: string,
  ) => {
    setMessages((previous) => [
      ...previous,
      {
        id:
          `${Date.now()}-${Math.random()}`,
        role,
        content,
      },
    ]);
  };


  const handleTopic = async (
    topic: string,
  ) => {
    setError("");
    setLoading(true);

    addMessage(
      "user",
      topic,
    );

    try {
      const validation =
        await validateTopic(topic);

      if (!validation.valid) {
        throw new ApiError(
          validation.message ||
            "Please provide a valid health topic.",
          400,
        );
      }

      const normalizedTopic =
        validation.topic ||
        topic;

      const summary =
        await generateSummary(
          normalizedTopic,
        );

      addMessage(
        "assistant",
        summary.summary,
      );

      const quiz =
        await generateQuiz(
          summary.summary,
        );

      addMessage(
        "assistant",
        `Quiz:\n\n${quiz.question}`,
      );

    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again.";

      setError(message);

      addMessage(
        "assistant",
        message,
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <div
      className="
        flex min-h-screen
        flex-col
      "
      style={{
        background:
          "var(--background)",
        color:
          "var(--foreground)",
      }}
    >
      <Header />

      <main
        className="
          mx-auto flex w-full
          max-w-5xl flex-1
          flex-col
          px-4 sm:px-6
        "
      >
        {/* Empty state */}
        {messages.length === 0 && (
          <section
            className="
              flex flex-1
              flex-col
              items-center
              justify-center
              py-16
            "
          >
            <div
              className="
                mb-6
                flex h-16 w-16
                items-center justify-center
                rounded-2xl
                text-3xl
                font-bold
              "
              style={{
                background:
                  "var(--primary)",
                color:
                  "var(--primary-foreground)",
              }}
            >
              +
            </div>

            <h2
              className="
                text-center
                text-3xl
                font-semibold
                tracking-tight
              "
            >
              How can I help you
              learn about your health?
            </h2>

            <p
              className="
                mt-3
                max-w-xl
                text-center
                text-sm
                leading-6
              "
              style={{
                color:
                  "var(--muted-foreground)",
              }}
            >
              Ask about a health topic and
              HealthBot will search for
              relevant information and
              explain it in patient-friendly
              language.
            </p>

            <div
              className="
                mt-8
                grid w-full
                max-w-2xl
                grid-cols-1
                gap-3
                sm:grid-cols-3
              "
            >
              {[
                "Diabetes",
                "Headache",
                "Hypertension",
              ].map((topic) => (
                <button
                  key={topic}
                  type="button"
                  onClick={() =>
                    handleTopic(topic)
                  }
                  disabled={loading}
                  className="
                    rounded-2xl
                    border
                    px-4 py-4
                    text-left
                    text-sm
                    transition
                    hover:-translate-y-0.5
                    hover:shadow-md
                  "
                  style={{
                    background:
                      "var(--card)",
                    borderColor:
                      "var(--border)",
                  }}
                >
                  <span
                    className="font-medium"
                  >
                    Learn about
                  </span>

                  <span
                    className="mt-1 block"
                    style={{
                      color:
                        "var(--muted-foreground)",
                    }}
                  >
                    {topic}
                  </span>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Messages */}
        {messages.length > 0 && (
          <section
            className="
              flex-1
              space-y-6
              py-8
            "
          >
            {messages.map(
              (message) => (
                <div
                  key={message.id}
                  className={`
                    flex
                    ${
                      message.role ===
                      "user"
                        ? "justify-end"
                        : "justify-start"
                    }
                  `}
                >
                  <div
                    className="
                      max-w-3xl
                      rounded-3xl
                      px-5 py-4
                      text-sm
                      leading-7
                      whitespace-pre-wrap
                    "
                    style={{
                      background:
                        message.role ===
                        "user"
                          ? "var(--user-message)"
                          : "var(--assistant-message)",

                      border:
                        message.role ===
                        "assistant"
                          ? "1px solid var(--border)"
                          : "none",
                    }}
                  >
                    {message.content}
                  </div>
                </div>
              ),
            )}

            {loading && (
              <div
                className="
                  flex
                  justify-start
                "
              >
                <div
                  className="
                    rounded-3xl
                    border
                    px-5 py-4
                    text-sm
                  "
                  style={{
                    background:
                      "var(--card)",
                    borderColor:
                      "var(--border)",
                    color:
                      "var(--muted-foreground)",
                  }}
                  aria-live="polite"
                >
                  HealthBot is thinking...
                </div>
              </div>
            )}
          </section>
        )}

        {/* Error */}
        {error && (
          <div
            className="
              mb-4
              rounded-xl
              border
              px-4 py-3
              text-sm
            "
            role="alert"
            style={{
              background:
                "var(--danger-background)",
              borderColor:
                "var(--danger)",
              color:
                "var(--danger)",
            }}
          >
            {error}
          </div>
        )}

        {/* Input */}
        <div
          className="
            sticky bottom-0
            py-4
          "
          style={{
            background:
              "var(--background)",
          }}
        >
          <TopicInput
            onSubmit={handleTopic}
            disabled={loading}
          />
        </div>
      </main>

      <Footer />
    </div>
  );
}