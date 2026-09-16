"use client";

import {
  FormEvent,
} from "react";

type TopicInputProps = {
  value: string;
  onChange: (
    value: string,
  ) => void;
  onSubmit: (
    event: FormEvent,
  ) => void;
  disabled?: boolean;
};

export default function TopicInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
}: TopicInputProps) {
  return (
    <form
      onSubmit={onSubmit}
      className="w-full"
    >
      <label
        htmlFor="health-topic"
        className="sr-only"
      >
        Health topic
      </label>

      <div className="flex flex-col gap-3 sm:flex-row">
        <textarea
          id="health-topic"
          value={value}
          onChange={(event) =>
            onChange(
              event.target.value,
            )
          }
          disabled={disabled}
          maxLength={200}
          rows={2}
          placeholder="Ask about a health topic..."
          aria-describedby="topic-help"
          className="min-h-14 flex-1 resize-none rounded-xl border p-3"
        />

        <button
          type="submit"
          disabled={
            disabled ||
            !value.trim()
          }
          className="rounded-xl border px-5 py-3 sm:self-end"
        >
          Ask HealthBot
        </button>
      </div>

      <p
        id="topic-help"
        className="mt-2 text-xs opacity-60"
      >
        Enter a health topic for
        patient-friendly educational
        information.
      </p>
    </form>
  );
}