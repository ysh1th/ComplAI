"use client";

import { useState } from "react";
import type { ComplianceData } from "@/lib/types";
import { VersionLabel } from "./VersionLabel";
import { BookOpen, FileText, Shield, ChevronDown, ChevronRight, Sparkles } from "lucide-react";

interface ComplianceSummaryProps {
  data: ComplianceData;
}

export function ComplianceSummary({ data }: ComplianceSummaryProps) {
  const totalRegulations =
    data.old_regulations.length + data.new_regulations.length;
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    () => new Set(data.new_regulations.map((r) => r.regulation_update_id))
  );

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-deriv-red" />
          <h3 className="text-base font-bold text-white">
            {data.jurisdiction} Compliance Overview
          </h3>
        </div>
        <VersionLabel version={data.current_version} />
      </div>

      <p className="text-sm text-deriv-grey mb-4">
        Currently monitoring against{" "}
        <span className="text-white font-semibold">{totalRegulations}</span>{" "}
        regulations
      </p>

      {/* Old regulations */}
      <div className="mb-4">
        <div className="flex items-center gap-1.5 mb-2">
          <BookOpen className="w-4 h-4 text-deriv-grey" />
          <span className="text-xs text-deriv-grey uppercase tracking-wider font-semibold">
            Foundational Regulations ({data.old_regulations.length})
          </span>
        </div>
        <div className="space-y-2">
          {data.old_regulations.map((reg) => (
            <div
              key={reg.regulation_update_id}
              className="flex items-start gap-2 text-sm"
            >
              <FileText className="w-3.5 h-3.5 text-deriv-grey mt-0.5 shrink-0" />
              <div>
                <span className="text-white font-medium">
                  {reg.update_title}
                </span>
                <span className="text-deriv-grey"> — {reg.date_effective}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* New / Pushed regulations */}
      {data.new_regulations.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <BookOpen className="w-4 h-4 text-deriv-teal" />
            <span className="text-xs text-deriv-teal uppercase tracking-wider font-semibold">
              Pushed Regulations ({data.new_regulations.length})
            </span>
          </div>
          <div className="space-y-2">
            {data.new_regulations.map((reg) => {
              const isExpanded = expandedIds.has(reg.regulation_update_id);
              return (
                <div
                  key={reg.regulation_update_id}
                  className="rounded-lg border border-deriv-teal/20 bg-deriv-teal/5 p-3 transition-colors"
                >
                  <button
                    onClick={() => toggleExpand(reg.regulation_update_id)}
                    className="flex items-start gap-2 text-sm w-full text-left group"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-3.5 h-3.5 text-deriv-teal mt-0.5 shrink-0" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 text-deriv-teal mt-0.5 shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-white font-medium group-hover:text-deriv-teal transition-colors">
                          {reg.update_title}
                        </span>
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-deriv-teal/20 text-deriv-teal">
                          <Sparkles className="w-2.5 h-2.5" />
                          New
                        </span>
                      </div>
                      <span className="text-deriv-grey text-xs">
                        {reg.date_effective}
                      </span>
                    </div>
                  </button>
                  {isExpanded && reg.summary && (
                    <div className="mt-2 ml-[22px] pl-1 border-l-2 border-deriv-teal/30">
                      <p className="text-xs text-deriv-grey/90 leading-relaxed pl-2">
                        {reg.summary}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
