import { Sparkles } from "lucide-react";

export default function LoadingState({
  message = "Thinking...",
}: {
  message?: string;
}) {
  return (
    <div className="animate-in flex items-center gap-3 py-6">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-50 text-teal-700">
        <Sparkles
          size={17}
          className="animate-pulse"
        />
      </div>

      <div>
        <p className="text-sm font-medium text-slate-700">
          {message}
        </p>

        <p className="mt-0.5 text-xs text-slate-400">
          This may take a few seconds.
        </p>
      </div>
    </div>
  );
}