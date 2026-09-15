interface SessionDecisionProps {
  onContinue: () => void;
  onFinish: () => void;
}

export default function SessionDecision({
  onContinue,
  onFinish,
}: SessionDecisionProps) {
  return (
    <section className="rounded-2xl border bg-white p-6 text-center shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">
        Continue learning?
      </h2>

      <p className="mt-2 text-sm text-slate-500">
        Explore another health topic or finish
        your session.
      </p>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <button
          onClick={onContinue}
          className="flex-1 rounded-xl bg-slate-900 px-5 py-3 font-medium text-white hover:bg-slate-800"
        >
          Learn another topic
        </button>

        <button
          onClick={onFinish}
          className="flex-1 rounded-xl border border-slate-300 px-5 py-3 font-medium text-slate-700 hover:bg-slate-50"
        >
          Finish session
        </button>
      </div>
    </section>
  );
}