import { AlertCircle, X } from "lucide-react";

export default function ErrorMessage({
  message,
}: {
  message: string;
}) {
  return (
    <div className="animate-in flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50/80 p-4">
      <div className="mt-0.5 rounded-full bg-red-100 p-1.5 text-red-600">
        <AlertCircle size={16} />
      </div>

      <div className="flex-1">
        <p className="text-sm font-medium text-red-800">
          Something went wrong
        </p>

        <p className="mt-1 text-sm leading-6 text-red-700">
          {message}
        </p>
      </div>

      <X
        size={17}
        className="text-red-400"
      />
    </div>
  );
}