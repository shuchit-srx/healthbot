import {
  Award,
  CheckCircle2,
} from "lucide-react";

export default function GradeCard({
  grade,
  feedback,
}: {
  grade: string;
  feedback: string;
}) {
  const isPositive =
    grade === "A" || grade === "B";

  return (
    <section className="animate-in mt-8">
      <div className="flex items-start gap-4">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
            isPositive
              ? "bg-teal-50 text-teal-700"
              : "bg-amber-50 text-amber-700"
          }`}
        >
          <Award size={19} />
        </div>

        <div className="min-w-0 flex-1">
          <p className="font-semibold text-slate-900">
            Quiz result
          </p>

          <div className="mt-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-bold ${
                  isPositive
                    ? "bg-teal-50 text-teal-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {grade}
              </div>

              <div>
                <p className="text-sm font-medium text-slate-800">
                  Your understanding
                </p>

                <p className="text-xs text-slate-500">
                  Based on your answer and the
                  education provided.
                </p>
              </div>
            </div>

            <div className="mt-5 border-t border-slate-100 pt-5">
              <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700">
                <CheckCircle2 size={15} />
                Feedback
              </div>

              <div className="whitespace-pre-line text-sm leading-7 text-slate-600">
                {feedback}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}