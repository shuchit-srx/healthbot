"use client";

import {
  ArrowUp,
} from "lucide-react";
import {
  KeyboardEvent,
  useEffect,
  useRef,
} from "react";

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function TopicInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
  placeholder = "Ask about a health topic...",
}: TopicInputProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const height = Math.min(
      textarea.scrollHeight,
      150,
    );

    textarea.style.height = `${height}px`;
  }, [value]);

  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (!disabled && value.trim()) {
        onSubmit();
      }
    }
  }

  return (
    <div className="topic-input-wrapper">
      <div className="topic-input">
        <textarea
          ref={textareaRef}
          className="topic-textarea"
          value={value}
          onChange={(event) =>
            onChange(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          maxLength={200}
          disabled={disabled}
          rows={1}
          aria-label="Health topic"
        />

        <button
          type="button"
          className="ask-button"
          onClick={onSubmit}
          disabled={
            disabled || !value.trim()
          }
          aria-label="Ask HealthBot"
        >
          <ArrowUp size={19} />

          <span className="ask-button-text">
            Ask
          </span>
        </button>
      </div>
    </div>
  );
}