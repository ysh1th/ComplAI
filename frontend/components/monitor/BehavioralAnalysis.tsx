"use client";

import type { UserBaseline, PreprocessedTransaction } from "@/lib/types";
import { StatisticalBrain } from "./StatisticalBrain";
import { PhysicsBrain } from "./PhysicsBrain";

interface BehavioralAnalysisProps {
  baseline: UserBaseline;
  preprocessed: PreprocessedTransaction;
}

export function BehavioralAnalysis({
  baseline,
  preprocessed,
}: BehavioralAnalysisProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-deriv-grey uppercase tracking-wider">
        Behavioral Analysis
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <StatisticalBrain baseline={baseline} preprocessed={preprocessed} />
        <PhysicsBrain preprocessed={preprocessed} />
      </div>
    </div>
  );
}
