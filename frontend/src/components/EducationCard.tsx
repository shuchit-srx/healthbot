import { BookOpen } from "lucide-react";

export default function EducationCard({
  topic,
  summary,
}: {
  topic: string;
  summary: string;
}) {
  return (
    <section className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-start gap-3">
        <div className="rounded-xl bg-slate-100 p-2">
          <BookOpen size={20} />
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Health topic
          </p>

          <h2 className="text-xl font-bold capitalize text-slate-900">
            {topic}
          </h2>
        </div>
      </div>

      <div className="whitespace-pre-line leading-7 text-slate-700">
        {summary}
      </div>
    </section>
  );
}