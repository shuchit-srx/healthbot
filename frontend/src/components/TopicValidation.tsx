import { Check } from "lucide-react";

export default function TopicValidation({
  topic,
}: {
  topic: string;
}) {
  return (
    <div className="animate-in flex items-center gap-2 text-sm text-slate-500">
      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-teal-50 text-teal-700">
        <Check size={14} />
      </div>

      <span>
        Learning about{" "}
        <span className="font-medium text-slate-800">
          {topic}
        </span>
      </span>
    </div>
  );
}