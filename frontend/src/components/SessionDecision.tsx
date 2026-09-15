import {
  ArrowRight,
  Plus,
} from "lucide-react";

interface SessionDecisionProps {
  onContinue: () => void;
  onFinish: () => void;
}

export default function SessionDecision({
  onContinue,
  onFinish,
}: SessionDecisionProps) {
  return (
    <section className="animate-in ml-0 mt-6 sm:ml-13">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-sm font-medium text-slate-800">
          What would you like to do next?
        </p>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <button
            onClick={onContinue}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-700"
          >
            <Plus size={16} />
            Learn another topic
          </button>

          <button
            onClick={onFinish}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Finish session
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </section>
  );
}