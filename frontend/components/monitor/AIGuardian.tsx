"use client";

import type { FullAnalysisResponse } from "@/lib/types";
import { AgentChainLog } from "@/components/shared/AgentChainLog";
import { Bot, Terminal, AlertTriangle, Shield } from "lucide-react";

interface AIGuardianProps {
  analysis: FullAnalysisResponse;
}

export function AIGuardian({ analysis }: AIGuardianProps) {
  const validatorLoops = analysis.validator_loops ?? 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Bot className="w-5 h-5 text-deriv-red" />
        <h3 className="text-sm font-semibold text-deriv-grey uppercase tracking-wider">
          AI Guardian
        </h3>
      </div>

      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <h4 className="text-sm font-semibold text-white mb-3">Agent Chain</h4>
        <AgentChainLog chain={analysis.agent_chain} />
      </div>

      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-2.5 bg-black/30 border-b border-deriv-dark-border">
          <Terminal className="w-4 h-4 text-deriv-teal" />
          <span className="text-xs font-mono text-deriv-teal">
            anomaly_detector.analysis
          </span>
          {validatorLoops > 0 && (
            <span className="inline-flex items-center gap-1 ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Shield className="w-2.5 h-2.5" />
              Refined x{validatorLoops}
            </span>
          )}
          <div className="w-1.5 h-1.5 bg-deriv-teal rounded-full animate-blink ml-auto" />
        </div>
        <div className="p-5">
          <p className="text-sm font-mono text-deriv-grey leading-relaxed whitespace-pre-wrap">
            {analysis.reasoning}
          </p>

          {validatorLoops > 0 && (
            <div className="mt-4 pt-3 border-t border-deriv-dark-border">
              <p className="text-xs text-purple-400/80 italic flex items-center gap-1.5">
                <Shield className="w-3 h-3" />
                Analysis refined {validatorLoops} time{validatorLoops > 1 ? "s" : ""} by
                the Internal Validator to ensure regulatory accuracy.
              </p>
            </div>
          )}
        </div>
      </div>

      {analysis.flags.length > 0 && (
        <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
          <h4 className="text-sm font-semibold text-white mb-3">
            Triggered Flags ({analysis.flags.length})
          </h4>
          <div className="space-y-2">
            {analysis.flags.map((flag, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 text-sm text-deriv-grey"
              >
                <AlertTriangle className="w-4 h-4 text-deriv-red mt-0.5 shrink-0" />
                <span>{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {analysis.regulations_violated.length > 0 && (
        <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
          <h4 className="text-sm font-semibold text-white mb-3">
            Regulations Violated ({analysis.regulations_violated.length})
          </h4>
          <div className="space-y-2">
            {analysis.regulations_violated.map((reg, i) => (
              <div key={i} className="text-sm">
                <span className="text-deriv-red font-medium">{reg}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
