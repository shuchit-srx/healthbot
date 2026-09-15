export default function LoadingState({
  message = "Processing...",
}: {
  message?: string;
}) {
  return (
    <div className="flex items-center justify-center gap-3 py-8">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />

      <p className="text-sm text-slate-600">
        {message}
      </p>
    </div>
  );
}