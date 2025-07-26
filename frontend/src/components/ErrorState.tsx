import { AlertCircle } from "lucide-react";

export function ErrorState({ 
  message = "Something went wrong", 
  onRetry 
}: { 
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-red-500">
      <AlertCircle className="w-8 h-8 mb-2" />
      <p className="text-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
