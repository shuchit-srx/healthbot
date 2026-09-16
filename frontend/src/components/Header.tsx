"use client";

import { useState } from "react";

export default function Header() {
  const [darkMode, setDarkMode] =
    useState(false);

  const toggleTheme = () => {
    const nextMode = !darkMode;

    setDarkMode(nextMode);

    document.documentElement.classList.toggle(
      "dark",
      nextMode,
    );
  };

  return (
    <header
      className="
        sticky top-0 z-50
        border-b
        backdrop-blur-xl
      "
      style={{
        background:
          "color-mix(in srgb, var(--background) 88%, transparent)",
        borderColor: "var(--border)",
      }}
    >
      <div
        className="
          mx-auto flex h-16
          max-w-7xl
          items-center justify-between
          px-4 sm:px-6 lg:px-8
        "
      >
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="
              flex h-9 w-9
              items-center justify-center
              rounded-xl
              text-lg
              font-bold
            "
            style={{
              background: "var(--primary)",
              color: "var(--primary-foreground)",
            }}
          >
            +
          </div>

          <div>
            <h1
              className="
                text-lg font-semibold
                tracking-tight
              "
            >
              HealthBot
            </h1>

            <p
              className="hidden text-xs sm:block"
              style={{
                color:
                  "var(--muted-foreground)",
              }}
            >
              Your health education assistant
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="
              flex h-10 w-10
              items-center justify-center
              rounded-full
              border
              transition
              hover:scale-105
            "
            style={{
              borderColor: "var(--border)",
              background: "var(--card)",
            }}
          >
            {darkMode ? "☀" : "☾"}
          </button>

          <button
            type="button"
            aria-label="Profile"
            className="
              flex h-10 w-10
              items-center justify-center
              rounded-full
              text-sm font-semibold
            "
            style={{
              background: "var(--muted)",
              color: "var(--foreground)",
            }}
          >
            G
          </button>
        </div>
      </div>
    </header>
  );
}