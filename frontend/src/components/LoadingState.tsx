import { Loader2 } from "lucide-react";

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-gray-500">
      <Loader2 className="w-8 h-8 animate-spin mb-2" />
      <p className="text-sm">{message}</p>
    </div>
  );
}
