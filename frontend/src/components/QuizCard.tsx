"use client";

import { HelpCircle } from "lucide-react";
import { useState } from "react";

interface QuizCardProps {
  question: string;
  onSubmit: (answer: string) => void;
  loading: boolean;
}

export default function QuizCard({
  question,
  onSubmit,
  loading,
}: QuizCardProps) {
  const [answer, setAnswer] = useState("");

  function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmedAnswer = answer.trim();

    if (!trimmedAnswer || loading) {
      return;
    }

    onSubmit(trimmedAnswer);
  }

  return (
    <section className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="mb-5 flex gap-3">
        <div className="rounded-xl bg-slate-100 p-2">
          <HelpCircle size={20} />
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Comprehension check
          </p>

          <h2 className="text-lg font-semibold text-slate-900">
            Test what you learned
          </h2>
        </div>
      </div>

      <p className="mb-5 text-slate-700">
        {question}
      </p>

      <form
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        <textarea
          value={answer}
          onChange={(event) =>
            setAnswer(event.target.value)
          }
          placeholder="Write your answer..."
          rows={4}
          maxLength={2000}
          disabled={loading}
          className="w-full resize-none rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200 disabled:bg-slate-100"
        />

        <button
          type="submit"
          disabled={loading || !answer.trim()}
          className="w-full rounded-xl bg-slate-900 px-5 py-3 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Submit answer
        </button>
      </form>
    </section>
  );
}