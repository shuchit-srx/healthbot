"use client";

import {
  HeartPulse,
  Menu,
  Plus,
  ShieldCheck,
} from "lucide-react";

interface HeaderProps {
  onNewTopic?: () => void;
}

export default function Header({
  onNewTopic,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <button
            className="rounded-full p-2 text-slate-600 transition hover:bg-slate-100 lg:hidden"
            aria-label="Open menu"
          >
            <Menu size={21} />
          </button>

          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
              <HeartPulse size={20} />
            </div>

            <div>
              <h1 className="text-[17px] font-semibold tracking-tight text-slate-900">
                HealthBot
              </h1>

              <p className="hidden text-[11px] text-slate-500 sm:block">
                Patient Education AI
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onNewTopic && (
            <button
              onClick={onNewTopic}
              className="flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
            >
              <Plus size={17} />
              <span className="hidden sm:inline">
                New topic
              </span>
            </button>
          )}

          <div className="hidden items-center gap-2 rounded-full bg-teal-50 px-3 py-2 text-xs font-medium text-teal-700 sm:flex">
            <ShieldCheck size={15} />
            Education only
          </div>
        </div>
      </div>
    </header>
  );
}