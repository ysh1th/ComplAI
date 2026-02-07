"use client";

import type { UserBaseline, PreprocessedTransaction } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { BarChart3 } from "lucide-react";

interface StatisticalBrainProps {
  baseline: UserBaseline;
  preprocessed: PreprocessedTransaction;
}

export function StatisticalBrain({ baseline, preprocessed }: StatisticalBrainProps) {
  const comparisons = [
    {
      label: "Tx Amount",
      baseline: baseline.avg_tx_amount_usd,
      current: preprocessed.transaction_amount_usd,
      format: (v: number) => formatCurrency(v),
    },
    {
      label: "Daily Total",
      baseline: baseline.avg_daily_total_usd,
      current: preprocessed.daily_total_usd,
      format: (v: number) => formatCurrency(v),
    },
    {
      label: "Tx/Day",
      baseline: baseline.avg_tx_per_day,
      current: preprocessed.tx_count_per_day,
      format: (v: number) => `${v}`,
    },
  ];

  return (
    <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-deriv-teal" />
        <h4 className="text-sm font-semibold text-white">Deviation Monitor</h4>
      </div>

      <div className="space-y-4">
        {comparisons.map((comp) => {
          const ratio = comp.baseline > 0 ? comp.current / comp.baseline : 0;
          const isHigh = ratio > 2;
          const isMedium = ratio > 1.5;
          const barColor = isHigh
            ? "#FF444F"
            : isMedium
            ? "#F5A623"
            : "#00A79E";
          const baselineWidth = Math.min(
            (comp.baseline / Math.max(comp.current, comp.baseline)) * 100,
            100
          );
          const currentWidth = Math.min(
            (comp.current / Math.max(comp.current, comp.baseline)) * 100,
            100
          );

          return (
            <div key={comp.label}>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-deriv-grey">{comp.label}</span>
                <span className="text-white font-medium">
                  {ratio > 0 ? `${ratio.toFixed(1)}×` : "–"}
                </span>
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-deriv-grey w-14">
                    Avg
                  </span>
                  <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-deriv-grey/40 rounded-full"
                      style={{ width: `${baselineWidth}%` }}
                    />
                  </div>
                  <span className="text-xs text-deriv-grey w-20 text-right">
                    {comp.format(comp.baseline)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-deriv-grey w-14">
                    Current
                  </span>
                  <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${currentWidth}%`,
                        backgroundColor: barColor,
                      }}
                    />
                  </div>
                  <span
                    className="text-xs font-medium w-20 text-right"
                    style={{ color: barColor }}
                  >
                    {comp.format(comp.current)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
