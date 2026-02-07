"use client";

import type { Regulation } from "@/lib/types";
import { Zap, Calendar, FileText } from "lucide-react";

interface PushComplianceProps {
  regulations: Regulation[];
  pushing: boolean;
  pushingId: string | null;
  onPush: (regulationId: string) => void;
}

export function PushCompliance({
  regulations,
  pushing,
  pushingId,
  onPush,
}: PushComplianceProps) {
  if (regulations.length === 0) {
    return (
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-6 text-center">
        <p className="text-sm text-deriv-grey">
          All available regulations have been pushed for this jurisdiction.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-white flex items-center gap-2">
        <Zap className="w-5 h-5 text-deriv-amber" />
        Available New Regulations
      </h3>

      <div className="grid gap-4">
        {regulations.map((reg) => {
          const isThisPushing = pushing && pushingId === reg.regulation_update_id;
          return (
            <div
              key={reg.regulation_update_id}
              className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5 hover:border-deriv-red/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <FileText className="w-4 h-4 text-deriv-red shrink-0" />
                    <span className="text-sm font-bold text-white">
                      {reg.update_title}
                    </span>
                  </div>
                  <p className="text-sm text-deriv-grey leading-relaxed mb-2">
                    {reg.summary}
                  </p>
                  <div className="flex items-center gap-1.5 text-xs text-deriv-grey">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Effective: {reg.date_effective}</span>
                    <span className="mx-1">•</span>
                    <span className="text-deriv-grey/70">
                      {reg.regulation_update_id}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onPush(reg.regulation_update_id)}
                  disabled={pushing}
                  className="shrink-0 px-5 py-2.5 bg-deriv-red text-white text-sm font-bold rounded-lg hover:bg-deriv-red/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isThisPushing ? "Pushing..." : "Push"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
