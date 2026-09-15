import { ExternalLink } from "lucide-react";
import type { Source } from "@/src/types/healthbot";

export default function SourceList({
  sources,
}: {
  sources: Source[];
}) {
  if (!sources.length) {
    return null;
  }

  return (
    <section className="rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-900">
        Sources
      </h3>

      <div className="space-y-3">
        {sources.map((source, index) => (
          <a
            key={`${source.url}-${index}`}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start justify-between gap-4 rounded-xl border p-4 transition hover:bg-slate-50"
          >
            <div>
              <p className="font-medium text-slate-900">
                {source.title}
              </p>

              <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                {source.content}
              </p>
            </div>

            <ExternalLink
              size={18}
              className="mt-1 shrink-0 text-slate-500"
            />
          </a>
        ))}
      </div>
    </section>
  );
}