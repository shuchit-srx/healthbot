"use client";

import { useState } from "react";

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
  | "decision"
  | "finished";

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

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleTopicSubmit(
    submittedTopic: string
  ) {
    setLoading(true);
    setError("");

    try {
      const validation =
        await validateTopic(submittedTopic);

      if (!validation.valid) {
        setError(
          validation.message ||
            "The provided topic is not recognized."
        );
        return;
      }

      const normalizedTopic =
        validation.topic;

      setTopic(normalizedTopic);
      setStage("summary");

      const summary =
        await generateSummary(
          normalizedTopic
        );

      setSummaryData(summary);

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
          : "Unable to process the topic."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleAnswerSubmit(
    answer: string
  ) {
    if (!summaryData) {
      return;
    }

    setLoading(true);
    setError("");

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
      setLoading(false);
    }
  }

  async function handleContinue() {
    setLoading(true);
    setError("");

    try {
      await decideSession(true);

      setTopic("");
      setSummaryData(null);
      setQuizQuestion("");
      setGradeData(null);
      setStage("topic");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to continue the session."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleFinish() {
    setLoading(true);
    setError("");

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
      setLoading(false);
    }
  }

  function resetSession() {
    setTopic("");
    setSummaryData(null);
    setQuizQuestion("");
    setGradeData(null);
    setError("");
    setStage("topic");
  }

  return (
    <div className="space-y-6">
      {stage === "topic" && (
        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-900">
              What would you like to learn?
            </h2>

            <p className="mt-2 text-slate-500">
              Enter a health topic and HealthBot
              will find current information, explain
              it simply, and test your understanding.
            </p>
          </div>

          <TopicInput
            onSubmit={handleTopicSubmit}
            loading={loading}
          />
        </section>
      )}

      {loading && (
        <LoadingState
          message={
            stage === "summary"
              ? "Researching and preparing your explanation..."
              : "Processing your request..."
          }
        />
      )}

      {error && (
        <ErrorMessage message={error} />
      )}

      {stage !== "topic" &&
        stage !== "finished" &&
        topic && (
          <TopicValidation topic={topic} />
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

      {stage === "quiz" &&
        quizQuestion &&
        !loading && (
          <QuizCard
            question={quizQuestion}
            onSubmit={handleAnswerSubmit}
            loading={loading}
          />
        )}

      {stage === "grade" &&
        gradeData &&
        !loading && (
          <>
            <GradeCard
              grade={gradeData.grade}
              feedback={gradeData.feedback}
            />

            <SessionDecision
              onContinue={handleContinue}
              onFinish={handleFinish}
            />
          </>
        )}

      {stage === "finished" && (
        <section className="rounded-2xl border bg-white p-8 text-center shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900">
            Session complete
          </h2>

          <p className="mt-2 text-slate-500">
            Thanks for learning with HealthBot.
          </p>

          <button
            onClick={resetSession}
            className="mt-6 rounded-xl bg-slate-900 px-6 py-3 font-medium text-white hover:bg-slate-800"
          >
            Start another session
          </button>
        </section>
      )}
    </div>
  );
}