"use client";

import {
  ArrowUp,
  Brain,
  CheckCircle2,
} from "lucide-react";
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

    const trimmed = answer.trim();

    if (!trimmed || loading) {
      return;
    }

    onSubmit(trimmed);
  }

  return (
    <section className="animate-in mt-8">
      <div className="flex items-start gap-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-700">
          <Brain size={19} />
        </div>

        <div className="min-w-0 flex-1">
          <p className="font-semibold text-slate-900">
            Quick comprehension check
          </p>

          <div className="mt-3 rounded-2xl border border-blue-100 bg-blue-50/50 p-5">
            <p className="text-[15px] leading-7 text-slate-800">
              {question}
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="mt-4"
          >
            <div className="rounded-[24px] border border-slate-200 bg-white p-3 shadow-sm focus-within:border-slate-300 focus-within:shadow-md">
              <textarea
                value={answer}
                onChange={(event) =>
                  setAnswer(event.target.value)
                }
                placeholder="Write your answer..."
                rows={3}
                maxLength={2000}
                disabled={loading}
                className="w-full resize-none border-0 bg-transparent px-3 py-2 text-sm leading-6 text-slate-800 outline-none placeholder:text-slate-400"
              />

              <div className="flex items-center justify-between px-2 pb-1">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <CheckCircle2 size={13} />
                  Answer based on what you learned
                </div>

                <button
                  type="submit"
                  disabled={
                    loading || !answer.trim()
                  }
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
                  aria-label="Submit answer"
                >
                  <ArrowUp size={17} />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}