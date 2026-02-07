"use client";

import { useState, useEffect } from "react";
import type { Rulebook, RuleEntry } from "@/lib/types";
import {
  ChevronDown,
  ChevronRight,
  DollarSign,
  Repeat,
  MapPin,
  Brain,
  AlertTriangle,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ActiveRulebookProps {
  rulebook: Rulebook;
  version?: string;
  isUpdated?: boolean;
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  rules: string[];
  defaultOpen?: boolean;
  isUpdated?: boolean;
}

function RuleSection({ title, icon, rules, defaultOpen = false, isUpdated = false }: SectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  // Auto-open sections when rulebook is freshly updated
  useEffect(() => {
    if (isUpdated) setOpen(true);
  }, [isUpdated]);

  return (
    <div className="border-b border-deriv-dark-border last:border-b-0">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-5 py-3.5 text-left hover:bg-white/5 transition-colors"
      >
        {open ? (
          <ChevronDown className="w-4 h-4 text-deriv-grey shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-deriv-grey shrink-0" />
        )}
        {icon}
        <span className="text-sm font-semibold text-white flex-1">
          {title}
        </span>
        <span className="text-xs text-deriv-grey">{rules.length} rules</span>
      </button>
      {open && (
        <div className="px-5 pb-4 space-y-2 ml-6">
          {rules.map((rule, i) => (
            <p key={i} className="text-sm text-deriv-grey leading-relaxed">
              • {rule}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export function ActiveRulebook({ rulebook, version, isUpdated = false }: ActiveRulebookProps) {
  const [showScoring, setShowScoring] = useState(false);

  // Auto-open scoring table on fresh update
  useEffect(() => {
    if (isUpdated) setShowScoring(true);
  }, [isUpdated]);

  return (
    <div
      className={cn(
        "bg-deriv-dark-card rounded-xl border overflow-hidden transition-colors duration-700",
        isUpdated
          ? "border-deriv-teal/50 ring-1 ring-deriv-teal/20"
          : "border-deriv-dark-border"
      )}
    >
      <div
        className={cn(
          "px-5 py-4 border-b flex items-center justify-between transition-colors duration-700",
          isUpdated ? "border-deriv-teal/30 bg-deriv-teal/5" : "border-deriv-dark-border"
        )}
      >
        <div className="flex items-center gap-2">
          <h3 className="text-base font-bold text-white">Active Rulebook</h3>
          {version && (
            <span
              className={cn(
                "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                isUpdated
                  ? "bg-deriv-teal/20 text-deriv-teal"
                  : "bg-white/10 text-deriv-grey"
              )}
            >
              {version}
            </span>
          )}
          {isUpdated && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-deriv-teal/20 text-deriv-teal animate-pulse">
              <Sparkles className="w-2.5 h-2.5" />
              Updated
            </span>
          )}
        </div>
        {isUpdated && (
          <div className="flex items-center gap-1.5 text-xs text-deriv-teal">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Active for all profiling</span>
          </div>
        )}
      </div>

      <RuleSection
        title="Amount-Based Rules"
        icon={<DollarSign className="w-4 h-4 text-deriv-amber shrink-0" />}
        rules={rulebook.amount_based}
        defaultOpen
        isUpdated={isUpdated}
      />
      <RuleSection
        title="Frequency-Based Rules"
        icon={<Repeat className="w-4 h-4 text-deriv-teal shrink-0" />}
        rules={rulebook.frequency_based}
        isUpdated={isUpdated}
      />
      <RuleSection
        title="Location-Based Rules"
        icon={<MapPin className="w-4 h-4 text-deriv-red shrink-0" />}
        rules={rulebook.location_based}
        isUpdated={isUpdated}
      />
      <RuleSection
        title="Behavioural Pattern Rules"
        icon={<Brain className="w-4 h-4 text-purple-400 shrink-0" />}
        rules={rulebook.behavioural_pattern}
        isUpdated={isUpdated}
      />

      {/* Risk Scoring Table */}
      <div className="border-b border-deriv-dark-border last:border-b-0">
        <button
          onClick={() => setShowScoring(!showScoring)}
          className="flex items-center gap-2 w-full px-5 py-3.5 text-left hover:bg-white/5 transition-colors"
        >
          {showScoring ? (
            <ChevronDown className="w-4 h-4 text-deriv-grey shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-deriv-grey shrink-0" />
          )}
          <AlertTriangle className="w-4 h-4 text-deriv-red shrink-0" />
          <span className="text-sm font-semibold text-white flex-1">
            Risk Scoring ({rulebook.risk_score.range})
          </span>
        </button>
        {showScoring && (
          <div className="px-5 pb-4 ml-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-deriv-grey text-left">
                  <th className="pb-2 font-medium">Category</th>
                  <th className="pb-2 font-medium">Rule</th>
                  <th className="pb-2 font-medium text-right">Points</th>
                </tr>
              </thead>
              <tbody>
                {rulebook.risk_score.rules?.map(
                  (rule: RuleEntry, i: number) => (
                    <tr key={i} className="border-t border-deriv-dark-border/50">
                      <td className="py-2 text-deriv-amber font-medium">
                        {rule.category}
                      </td>
                      <td className="py-2 text-deriv-grey">{rule.rule}</td>
                      <td className="py-2 text-deriv-red font-bold text-right">
                        +{rule.points}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
            <p className="text-xs text-deriv-grey mt-3">
              Capping: {rulebook.risk_score.capping}
            </p>

            {/* Risk Bands */}
            <div className="mt-3 space-y-1.5">
              <p className="text-xs text-deriv-grey uppercase font-semibold">
                Risk Bands
              </p>
              {Object.entries(rulebook.risk_bands).map(([band, desc]) => (
                <div key={band} className="flex items-center gap-2 text-sm">
                  <span
                    className={cn(
                      "w-2.5 h-2.5 rounded-full",
                      band === "HIGH" && "bg-deriv-red",
                      band === "MEDIUM" && "bg-deriv-amber",
                      band === "LOW" && "bg-deriv-teal",
                      band === "CLEAN" && "bg-deriv-grey"
                    )}
                  />
                  <span className="text-white font-medium">{band}:</span>
                  <span className="text-deriv-grey">{desc as string}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
