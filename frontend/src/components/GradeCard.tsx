import { Award } from "lucide-react";

export default function GradeCard({
  grade,
  feedback,
}: {
  grade: string;
  feedback: string;
}) {
  return (
    <section className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center gap-3">
        <div className="rounded-xl bg-slate-100 p-2">
          <Award size={20} />
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Quiz result
          </p>

          <h2 className="text-xl font-bold text-slate-900">
            Grade: {grade}
          </h2>
        </div>
      </div>

      <div className="whitespace-pre-line leading-7 text-slate-700">
        {feedback}
      </div>
    </section>
  );
}