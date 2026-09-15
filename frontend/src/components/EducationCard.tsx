import {
  Bot,
  Sparkles,
} from "lucide-react";

export default function EducationCard({
  topic,
  summary,
}: {
  topic: string;
  summary: string;
}) {
  return (
    <article className="animate-in">
      <div className="mb-4 flex items-start gap-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-teal-50 to-blue-50 text-teal-700">
          <Bot size={19} />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-slate-900">
              HealthBot
            </h2>

            <span className="rounded-full bg-teal-50 px-2 py-0.5 text-[10px] font-medium text-teal-700">
              AI
            </span>
          </div>

          <p className="mt-0.5 text-xs text-slate-400">
            About {topic}
          </p>
        </div>
      </div>

      <div className="ml-0 sm:ml-13">
        <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200/70 sm:p-6">
          <div className="mb-4 flex items-center gap-2 text-xs font-medium text-teal-700">
            <Sparkles size={14} />
            Patient-friendly explanation
          </div>

          <div className="whitespace-pre-line text-[15px] leading-7 text-slate-700">
            {summary}
          </div>
        </div>
      </div>
    </article>
  );
}