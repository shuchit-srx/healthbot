import {
  ExternalLink,
  Link2,
} from "lucide-react";

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
    <section className="animate-in ml-0 mt-5 sm:ml-13">
      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
        <Link2 size={16} />
        Sources
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {sources.map((source, index) => (
          <a
            key={`${source.url}-${index}`}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group rounded-2xl border border-slate-200 bg-white p-4 transition hover:border-teal-200 hover:bg-teal-50/30"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="line-clamp-2 text-sm font-medium text-slate-800 group-hover:text-teal-700">
                  {source.title}
                </p>

                <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                  {source.content}
                </p>
              </div>

              <ExternalLink
                size={15}
                className="shrink-0 text-slate-400 transition group-hover:text-teal-600"
              />
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}