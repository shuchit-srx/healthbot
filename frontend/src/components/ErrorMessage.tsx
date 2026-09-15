import { AlertCircle } from "lucide-react";

export default function ErrorMessage({
  message,
}: {
  message: string;
}) {
  return (
    <div className="flex gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
      <AlertCircle
        size={20}
        className="mt-0.5 shrink-0"
      />

      <p className="text-sm">
        {message}
      </p>
    </div>
  );
}