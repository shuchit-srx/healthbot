"use client";

import {
  ArrowUp,
  HeartPulse,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

interface TopicInputProps {
  onSubmit: (topic: string) => void;
  loading: boolean;
}

const suggestions = [
  "Diabetes",
  "Hypertension",
  "Migraine",
  "Vitamin D deficiency",
];

export default function TopicInput({
  onSubmit,
  loading,
}: TopicInputProps) {
  const [topic, setTopic] = useState("");

  function submitTopic(value: string) {
    const trimmed = value.trim();

    if (!trimmed || loading) {
      return;
    }

    onSubmit(trimmed);
  }

  function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    submitTopic(topic);
  }

  return (
    <div className="w-full">
      <div className="mb-8 text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-50 to-blue-50 text-teal-700">
          <HeartPulse size={27} />
        </div>

        <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
          What would you like to learn?
        </h2>

        <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500 sm:text-base">
          Ask about a health topic and HealthBot will
          research it, explain it clearly, and check
          your understanding.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="group relative rounded-[26px] border border-slate-200 bg-white p-3 shadow-sm transition-all duration-200 focus-within:border-slate-300 focus-within:shadow-md">
          <textarea
            value={topic}
            onChange={(event) =>
              setTopic(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                submitTopic(topic);
              }
            }}
            placeholder="Ask about a health topic..."
            maxLength={200}
            disabled={loading}
            rows={2}
            className="w-full resize-none border-0 bg-transparent px-3 py-2 text-base text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
          />

          <div className="flex items-center justify-between px-2 pb-1">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Sparkles size={14} />
              AI-powered health education
            </div>

            <button
              type="submit"
              disabled={
                loading || !topic.trim()
              }
              className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
              aria-label="Submit topic"
            >
              <ArrowUp size={18} />
            </button>
          </div>
        </div>
      </form>

      <div className="mt-5 flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            disabled={loading}
            onClick={() => {
              setTopic(suggestion);
              submitTopic(suggestion);
            }}
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-600 transition hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700 disabled:opacity-50"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}