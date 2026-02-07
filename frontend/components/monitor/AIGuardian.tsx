"use client";

import type { FullAnalysisResponse } from "@/lib/types";
import { AgentChainLog } from "@/components/shared/AgentChainLog";
import { Bot, Terminal, AlertTriangle } from "lucide-react";

interface AIGuardianProps {
  analysis: FullAnalysisResponse;
}

export function AIGuardian({ analysis }: AIGuardianProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Bot className="w-5 h-5 text-deriv-red" />
        <h3 className="text-sm font-semibold text-deriv-grey uppercase tracking-wider">
          AI Guardian
        </h3>
      </div>

      {/* Agent Chain */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <h4 className="text-sm font-semibold text-white mb-3">Agent Chain</h4>
        <AgentChainLog chain={analysis.agent_chain} />
      </div>

      {/* Reasoning Terminal */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-2.5 bg-black/30 border-b border-deriv-dark-border">
          <Terminal className="w-4 h-4 text-deriv-teal" />
          <span className="text-xs font-mono text-deriv-teal">
            anomaly_detector.analysis
          </span>
          <div className="w-1.5 h-1.5 bg-deriv-teal rounded-full animate-blink ml-auto" />
        </div>
        <div className="p-5">
          <p className="text-sm font-mono text-deriv-grey leading-relaxed whitespace-pre-wrap">
            {analysis.reasoning}
          </p>
        </div>
      </div>

      {/* Flags */}
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

      {/* Regulations Violated */}
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
