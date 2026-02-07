"use client";

import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  text?: string;
  size?: "sm" | "md" | "lg";
}

export function LoadingSpinner({
  text = "Processing...",
  size = "md",
}: LoadingSpinnerProps) {
  const sizeMap = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-8 h-8" };

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <Loader2 className={`${sizeMap[size]} text-deriv-red animate-spin`} />
      {text && <p className="text-sm text-deriv-grey">{text}</p>}
    </div>
  );
}
