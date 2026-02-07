"use client";

import type { RiskBand } from "@/lib/types";
import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  band: RiskBand;
  size?: "sm" | "md";
}

export function RiskBadge({ band, size = "sm" }: RiskBadgeProps) {
  const colorClasses = {
    HIGH: "bg-deriv-red/15 text-deriv-red border-deriv-red/30",
    MEDIUM: "bg-deriv-amber/15 text-deriv-amber border-deriv-amber/30",
    LOW: "bg-deriv-teal/15 text-deriv-teal border-deriv-teal/30",
    CLEAN: "bg-deriv-grey/15 text-deriv-grey border-deriv-grey/30",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center font-semibold rounded-full border",
        colorClasses[band],
        size === "sm" ? "px-2.5 py-0.5 text-xs" : "px-3 py-1 text-sm"
      )}
    >
      {band}
    </span>
  );
}
