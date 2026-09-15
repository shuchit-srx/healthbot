import { HeartPulse } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-slate-900 p-2 text-white">
            <HeartPulse size={22} />
          </div>

          <div>
            <h1 className="text-lg font-bold text-slate-900">
              HealthBot
            </h1>

            <p className="text-xs text-slate-500">
              Patient Education Assistant
            </p>
          </div>
        </div>

        <span className="hidden text-sm text-slate-500 sm:block">
          Learn. Understand. Take control.
        </span>
      </div>
    </header>
  );
}