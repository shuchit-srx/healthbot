"use client";

import {
  FormEvent,
  useState,
} from "react";


interface TopicInputProps {
  onSubmit: (
    topic: string,
  ) => Promise<void>;

  disabled?: boolean;
}


export default function TopicInput({
  onSubmit,
  disabled = false,
}: TopicInputProps) {
  const [topic, setTopic] =
    useState("");


  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    const value = topic.trim();

    if (!value || disabled) {
      return;
    }

    await onSubmit(value);

    setTopic("");
  };


  return (
    <form
      onSubmit={handleSubmit}
      className="w-full"
    >
      <div
        className="
          flex items-end gap-2
          rounded-3xl
          border
          p-2
          shadow-sm
          transition
          focus-within:shadow-md
        "
        style={{
          borderColor: "var(--border)",
          background: "var(--card)",
        }}
      >
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

              event.currentTarget.form?.requestSubmit();
            }
          }}
          disabled={disabled}
          maxLength={200}
          rows={1}
          placeholder="Ask about a health topic..."
          aria-label="Health topic"
          className="
            max-h-32
            min-h-11
            flex-1
            resize-none
            bg-transparent
            px-4 py-3
            text-sm
            outline-none
          "
          style={{
            color: "var(--foreground)",
          }}
        />

        <button
          type="submit"
          disabled={
            disabled ||
            !topic.trim()
          }
          aria-label="Send message"
          className="
            flex h-11 w-11
            shrink-0
            items-center justify-center
            rounded-full
            text-lg
            font-semibold
            transition
            hover:scale-105
          "
          style={{
            background: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          ↑
        </button>
      </div>

      <p
        className="
          mt-2
          px-3
          text-xs
        "
        style={{
          color:
            "var(--muted-foreground)",
        }}
      >
        HealthBot provides educational information,
        not medical diagnosis.
      </p>
    </form>
  );
}