import { CheckCircle2 } from "lucide-react";

export default function TopicValidation({
  topic,
}: {
  topic: string;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 p-4 text-green-700">
      <CheckCircle2 size={20} />

      <div>
        <p className="text-sm font-medium">
          Topic recognized
        </p>

        <p className="text-sm">
          Learning about:{" "}
          <span className="font-semibold">
            {topic}
          </span>
        </p>
      </div>
    </div>
  );
}