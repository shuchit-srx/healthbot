"use client";

import { useState } from "react";
import {
  HeartPulse,
  MessageCircle,
  Plus,
  Sparkles,
} from "lucide-react";

import {
  decideSession,
  generateQuiz,
  generateSummary,
  gradeAnswer,
  validateTopic,
} from "@/src/lib/api";

import type {
  GradeResponse,
  SummaryResponse,
} from "@/src/types/healthbot";

import EducationCard from "./EducationCard";
import ErrorMessage from "./ErrorMessage";
import GradeCard from "./GradeCard";
import LoadingState from "./LoadingState";
import QuizCard from "./QuizCard";
import SessionDecision from "./SessionDecision";
import SourceList from "./SourceList";
import TopicInput from "./TopicInput";
import TopicValidation from "./TopicValidation";

type Stage =
  | "topic"
  | "summary"
  | "quiz"
  | "grade"
  | "finished";

type LoadingOperation =
  | "validating"
  | "researching"
  | "quiz"
  | "grading"
  | "session"
  | null;

export default function HealthBot() {
  const [stage, setStage] =
    useState<Stage>("topic");

  const [topic, setTopic] = useState("");

  const [summaryData, setSummaryData] =
    useState<SummaryResponse | null>(null);

  const [quizQuestion, setQuizQuestion] =
    useState("");

  const [gradeData, setGradeData] =
    useState<GradeResponse | null>(null);

  const [loadingOperation, setLoadingOperation] =
    useState<LoadingOperation>(null);

  const [error, setError] = useState("");

  const loading =
    loadingOperation !== null;

  function getLoadingMessage() {
    switch (loadingOperation) {
      case "validating":
        return "Validating your health topic...";

      case "researching":
        return "Researching medical information...";

      case "quiz":
        return "Generating your comprehension question...";

      case "grading":
        return "Evaluating your answer...";

      case "session":
        return "Updating your session...";

      default:
        return "Processing...";
    }
  }

  async function handleTopicSubmit(
    submittedTopic: string
  ) {
    setError("");
    setLoadingOperation("validating");

    try {
      const validation =
        await validateTopic(submittedTopic);

      if (!validation.valid) {
        setError(
          validation.message ||
            "The provided topic is not recognized as a health topic."
        );

        return;
      }

      const normalizedTopic =
        validation.topic;

      setTopic(normalizedTopic);
      setStage("summary");

      setLoadingOperation("researching");

      const summary =
        await generateSummary(
          normalizedTopic
        );

      setSummaryData(summary);

      setLoadingOperation("quiz");

      const quiz =
        await generateQuiz(
          summary.summary
        );

      setQuizQuestion(quiz.question);
      setStage("quiz");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to process the health topic."
      );
    } finally {
      setLoadingOperation(null);
    }
  }

  async function handleAnswerSubmit(
    answer: string
  ) {
    if (!summaryData) {
      setError(
        "Education content is unavailable."
      );
      return;
    }

    setError("");
    setLoadingOperation("grading");

    try {
      const result =
        await gradeAnswer(
          topic,
          summaryData.summary,
          quizQuestion,
          answer
        );

      setGradeData(result);
      setStage("grade");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to grade the answer."
      );
    } finally {
      setLoadingOperation(null);
    }
  }

  async function handleContinue() {
    setError("");
    setLoadingOperation("session");

    try {
      await decideSession(true);

      resetState();

      setStage("topic");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to continue the session."
      );
    } finally {
      setLoadingOperation(null);
    }
  }

  async function handleFinish() {
    setError("");
    setLoadingOperation("session");

    try {
      await decideSession(false);

      setStage("finished");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to finish the session."
      );
    } finally {
      setLoadingOperation(null);
    }
  }

  function resetState() {
    setTopic("");
    setSummaryData(null);
    setQuizQuestion("");
    setGradeData(null);
    setError("");
  }

  function resetSession() {
    resetState();
    setStage("topic");
  }

  return (
    <div className="flex min-h-[calc(100vh-64px)]">
      {/* Sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-slate-200/70 bg-white/60 px-3 py-4 lg:block">
        <button
          onClick={resetSession}
          className="mb-4 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
            <Plus size={17} />
          </div>

          New topic
        </button>

        <div className="px-3 py-3">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Your session
          </p>

          <div className="mt-4 flex items-center gap-3 rounded-xl bg-teal-50/70 px-3 py-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-teal-700 shadow-sm">
              <MessageCircle size={15} />
            </div>

            <div className="min-w-0">
              <p className="truncate text-xs font-medium text-slate-700">
                {topic || "New conversation"}
              </p>

              <p className="mt-0.5 text-[10px] text-slate-400">
                Health education
              </p>
            </div>
          </div>
        </div>

        <div className="mt-auto px-3 pb-2 pt-10">
          <div className="rounded-2xl bg-gradient-to-br from-teal-50 to-blue-50 p-4">
            <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg bg-white text-teal-700 shadow-sm">
              <HeartPulse size={16} />
            </div>

            <p className="text-xs font-semibold text-slate-700">
              Learn with confidence
            </p>

            <p className="mt-1 text-[11px] leading-5 text-slate-500">
              HealthBot uses current sources to create
              easy-to-understand educational content.
            </p>
          </div>
        </div>
      </aside>

      {/* Main conversation */}
      <main className="health-gradient flex min-w-0 flex-1 flex-col">
        <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-4 py-8 sm:px-6 lg:px-8">
          {stage === "topic" && (
            <div className="flex flex-1 items-center justify-center">
              <div className="w-full max-w-2xl">
                <TopicInput
                  onSubmit={handleTopicSubmit}
                  loading={loading}
                />
              </div>
            </div>
          )}

          {stage !== "topic" && (
            <div className="w-full">
              <div className="mb-8">
                <TopicValidation
                  topic={topic}
                />
              </div>

              {error && (
                <div className="mb-6">
                  <ErrorMessage
                    message={error}
                  />
                </div>
              )}

              {summaryData && (
                <>
                  <EducationCard
                    topic={summaryData.topic}
                    summary={summaryData.summary}
                  />

                  <SourceList
                    sources={summaryData.sources}
                  />
                </>
              )}

              {loading && (
                <LoadingState
                  message={getLoadingMessage()}
                />
              )}

              {stage === "quiz" &&
                quizQuestion &&
                !loading && (
                  <QuizCard
                    question={quizQuestion}
                    onSubmit={
                      handleAnswerSubmit
                    }
                    loading={loading}
                  />
                )}

              {stage === "grade" &&
                gradeData &&
                !loading && (
                  <>
                    <GradeCard
                      grade={gradeData.grade}
                      feedback={
                        gradeData.feedback
                      }
                    />

                    <SessionDecision
                      onContinue={
                        handleContinue
                      }
                      onFinish={handleFinish}
                    />
                  </>
                )}

              {stage === "finished" && (
                <div className="animate-in flex min-h-[50vh] items-center justify-center">
                  <div className="w-full max-w-lg text-center">
                    <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-50 text-teal-700">
                      <HeartPulse size={27} />
                    </div>

                    <h2 className="text-2xl font-semibold text-slate-900">
                      Session complete
                    </h2>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      You have completed this HealthBot
                      learning session.
                    </p>

                    <button
                      onClick={
                        resetSession
                      }
                      className="mt-6 rounded-full bg-slate-900 px-6 py-3 text-sm font-medium text-white transition hover:bg-slate-700"
                    >
                      Start a new topic
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {stage !== "topic" &&
            stage !== "finished" &&
            !loading && (
              <div className="mt-auto pt-10">
                <div className="mx-auto max-w-2xl">
                  <div className="rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-center text-xs text-slate-400 shadow-sm backdrop-blur">
                    <Sparkles
                      size={13}
                      className="mr-1 inline"
                    />
                    HealthBot provides educational
                    information, not medical diagnosis.
                  </div>
                </div>
              </div>
            )}
        </div>
      </main>
    </div>
  );
}