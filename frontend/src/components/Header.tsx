"use client";

import {
  HeartPulse,
  Moon,
  Sun,
} from "lucide-react";
import { useState } from "react";

type Theme = "light" | "dark";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const savedTheme =
    window.localStorage.getItem(
      "healthbot-theme",
    );

  if (
    savedTheme === "light" ||
    savedTheme === "dark"
  ) {
    return savedTheme;
  }

  return window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches
    ? "dark"
    : "light";
}

export default function Header() {
  const [theme, setTheme] =
    useState<Theme>(getInitialTheme);

  function applyTheme(
    nextTheme: Theme,
  ) {
    setTheme(nextTheme);

    document.documentElement.classList.toggle(
      "dark",
      nextTheme === "dark",
    );

    window.localStorage.setItem(
      "healthbot-theme",
      nextTheme,
    );
  }

  function toggleTheme() {
    applyTheme(
      theme === "light"
        ? "dark"
        : "light",
    );
  }

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark">
          <HeartPulse
            size={21}
            strokeWidth={2.2}
          />
        </div>

        <div className="brand-text">
          <span className="brand-name">
            HealthBot
          </span>

          <span className="brand-subtitle">
            AI-powered health education
          </span>
        </div>
      </div>

      <div className="header-actions">
        <button
          type="button"
          className="icon-button"
          onClick={toggleTheme}
          aria-label={
            theme === "light"
              ? "Switch to dark theme"
              : "Switch to light theme"
          }
          title={
            theme === "light"
              ? "Dark theme"
              : "Light theme"
          }
        >
          {theme === "light" ? (
            <Moon size={20} />
          ) : (
            <Sun size={20} />
          )}
        </button>
      </div>
    </header>
  );
}