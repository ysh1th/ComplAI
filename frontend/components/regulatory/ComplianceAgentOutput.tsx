"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import type { CompliancePushResponse, RuleEntry } from "@/lib/types";
import { AgentChainLog } from "@/components/shared/AgentChainLog";
import {
  FileText,
  GitCompare,
  BarChart3,
  Pencil,
  Bot,
  BookOpen,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  DollarSign,
  Repeat,
  MapPin,
  Brain,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ComplianceAgentOutputProps {
  result: CompliancePushResponse;
}

function UpdatedRuleSection({
  title,
  icon,
  rules,
}: {
  title: string;
  icon: React.ReactNode;
  rules: string[];
}) {
  const [open, setOpen] = useState(true);

  return (
    <div className="border-b border-deriv-teal/20 last:border-b-0">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-4 py-3 text-left hover:bg-deriv-teal/5 transition-colors"
      >
        {open ? (
          <ChevronDown className="w-3.5 h-3.5 text-deriv-teal shrink-0" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-deriv-teal shrink-0" />
        )}
        {icon}
        <span className="text-sm font-semibold text-white flex-1">
          {title}
        </span>
        <span className="text-xs text-deriv-teal font-medium">
          {rules.length} rules
        </span>
      </button>
      {open && (
        <div className="px-4 pb-3 space-y-1.5 ml-6">
          {rules.map((rule, i) => (
            <p key={i} className="text-sm text-deriv-grey leading-relaxed">
              <span className="text-deriv-teal mr-1.5">+</span>
              {rule}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export function ComplianceAgentOutput({ result }: ComplianceAgentOutputProps) {
  const [showUpdatedRulebook, setShowUpdatedRulebook] = useState(true);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      <div className="flex items-center gap-2">
        <Bot className="w-5 h-5 text-deriv-red" />
        <h3 className="text-base font-bold text-white">
          Compliance Agent Output
        </h3>
      </div>

      {/* Agent Chain */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <h4 className="text-sm font-semibold text-white mb-3">Agent Chain</h4>
        <AgentChainLog chain={result.agent_chain} />
      </div>

      {/* Summarizer Output */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-5 h-5 text-deriv-teal" />
          <h4 className="text-sm font-semibold text-white">Summary</h4>
        </div>
        <p className="text-sm text-deriv-grey leading-relaxed">
          {result.summary}
        </p>
      </div>

      {/* Comparison Output */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <GitCompare className="w-5 h-5 text-deriv-amber" />
          <h4 className="text-sm font-semibold text-white">
            Comparison Points ({result.comparison_points.length})
          </h4>
        </div>
        <div className="space-y-2.5">
          {result.comparison_points.map((point, i) => (
            <div key={i} className="flex items-start gap-2.5 text-sm">
              <span className="text-deriv-amber font-bold mt-0.5 shrink-0">
                {i + 1}.
              </span>
              <span className="text-deriv-grey leading-relaxed">{point}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Impact Analysis */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-5 h-5 text-deriv-red" />
          <h4 className="text-sm font-semibold text-white">Impact Analysis</h4>
        </div>
        <p className="text-sm text-deriv-grey leading-relaxed">
          {result.impact_analysis}
        </p>
      </div>

      {/* Rulebook Changes Description */}
      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <Pencil className="w-5 h-5 text-deriv-teal" />
          <h4 className="text-sm font-semibold text-white">
            Rulebook Changes
          </h4>
        </div>
        <p className="text-sm text-deriv-grey leading-relaxed">
          {result.rulebook_changes}
        </p>
      </div>

      {/* Updated Rulebook (Full) */}
      {result.updated_rulebook && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-deriv-dark-card rounded-xl border border-deriv-teal/30 overflow-hidden"
        >
          <button
            onClick={() => setShowUpdatedRulebook(!showUpdatedRulebook)}
            className="w-full px-5 py-4 flex items-center justify-between border-b border-deriv-teal/20 hover:bg-deriv-teal/5 transition-colors"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-deriv-teal" />
              <h4 className="text-sm font-bold text-white">
                Updated Rulebook — {result.new_version}
              </h4>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-deriv-teal/20 text-deriv-teal">
                Active
              </span>
            </div>
            {showUpdatedRulebook ? (
              <ChevronDown className="w-4 h-4 text-deriv-grey" />
            ) : (
              <ChevronRight className="w-4 h-4 text-deriv-grey" />
            )}
          </button>

          {showUpdatedRulebook && (
            <div>
              <UpdatedRuleSection
                title="Amount-Based Rules"
                icon={
                  <DollarSign className="w-4 h-4 text-deriv-amber shrink-0" />
                }
                rules={result.updated_rulebook.amount_based}
              />
              <UpdatedRuleSection
                title="Frequency-Based Rules"
                icon={
                  <Repeat className="w-4 h-4 text-deriv-teal shrink-0" />
                }
                rules={result.updated_rulebook.frequency_based}
              />
              <UpdatedRuleSection
                title="Location-Based Rules"
                icon={
                  <MapPin className="w-4 h-4 text-deriv-red shrink-0" />
                }
                rules={result.updated_rulebook.location_based}
              />
              <UpdatedRuleSection
                title="Behavioural Pattern Rules"
                icon={
                  <Brain className="w-4 h-4 text-purple-400 shrink-0" />
                }
                rules={result.updated_rulebook.behavioural_pattern}
              />

              {/* Risk Scoring */}
              {result.updated_rulebook.risk_score?.rules && (
                <div className="px-4 py-3 border-b border-deriv-teal/20">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4 text-deriv-red shrink-0" />
                    <span className="text-sm font-semibold text-white">
                      Risk Scoring ({result.updated_rulebook.risk_score.range})
                    </span>
                  </div>
                  <table className="w-full text-sm ml-6">
                    <thead>
                      <tr className="text-deriv-grey text-left">
                        <th className="pb-2 font-medium">Category</th>
                        <th className="pb-2 font-medium">Rule</th>
                        <th className="pb-2 font-medium text-right">Points</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.updated_rulebook.risk_score.rules.map(
                        (rule: RuleEntry, i: number) => (
                          <tr
                            key={i}
                            className="border-t border-deriv-dark-border/50"
                          >
                            <td className="py-2 text-deriv-amber font-medium">
                              {rule.category}
                            </td>
                            <td className="py-2 text-deriv-grey">
                              {rule.rule}
                            </td>
                            <td className="py-2 text-deriv-red font-bold text-right">
                              +{rule.points}
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Risk Bands */}
              {result.updated_rulebook.risk_bands && (
                <div className="px-4 py-3">
                  <div className="ml-6 space-y-1.5">
                    <p className="text-xs text-deriv-grey uppercase font-semibold mb-2">
                      Risk Bands
                    </p>
                    {Object.entries(result.updated_rulebook.risk_bands).map(
                      ([band, desc]) => (
                        <div
                          key={band}
                          className="flex items-center gap-2 text-sm"
                        >
                          <span
                            className={cn(
                              "w-2.5 h-2.5 rounded-full",
                              band === "HIGH" && "bg-deriv-red",
                              band === "MEDIUM" && "bg-deriv-amber",
                              band === "LOW" && "bg-deriv-teal",
                              band === "CLEAN" && "bg-deriv-grey"
                            )}
                          />
                          <span className="text-white font-medium">
                            {band}:
                          </span>
                          <span className="text-deriv-grey">
                            {desc as string}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      )}

      {/* Verification: New rulebook active for behavioral profiling */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-deriv-teal/5 rounded-xl border border-deriv-teal/30 p-5"
      >
        <div className="flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-deriv-teal shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-deriv-teal mb-1">
              Rulebook {result.new_version} Active for Behavioral Profiling
            </h4>
            <p className="text-xs text-deriv-grey leading-relaxed">
              The updated rulebook is now live. All future transaction monitoring,
              anomaly detection, and risk scoring for this jurisdiction will use
              the new {result.new_version} rules — including updated amount
              thresholds, frequency checks, location rules, and behavioural
              pattern analysis. Any transactions ingested from this point forward
              will be evaluated against these updated compliance rules.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
