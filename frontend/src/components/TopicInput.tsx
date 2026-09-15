"use client";

import { Search } from "lucide-react";
import { useState } from "react";

interface TopicInputProps {
  onSubmit: (topic: string) => void;
  loading: boolean;
}

export default function TopicInput({
  onSubmit,
  loading,
}: TopicInputProps) {
  const [topic, setTopic] = useState("");

  function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmedTopic = topic.trim();

    if (!trimmedTopic || loading) {
      return;
    }

    onSubmit(trimmedTopic);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4"
    >
      <div>
        <label
          htmlFor="topic"
          className="mb-2 block text-sm font-medium text-slate-700"
        >
          What would you like to learn about?
        </label>

        <input
          id="topic"
          type="text"
          value={topic}
          onChange={(event) =>
            setTopic(event.target.value)
          }
          placeholder="e.g. diabetes, hypertension..."
          maxLength={200}
          disabled={loading}
          className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200 disabled:cursor-not-allowed disabled:bg-slate-100"
        />
      </div>

      <button
        type="submit"
        disabled={loading || !topic.trim()}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Search size={18} />
        Learn about this topic
      </button>
    </form>
  );
}