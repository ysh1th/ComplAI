"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import type { CompliancePushResponse, RuleEntry, Rulebook } from "@/lib/types";
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
  Check,
  Clock,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ComplianceAgentOutputProps {
  result: CompliancePushResponse;
  onApprove?: (editedRulebook: Rulebook) => void;
  approving?: boolean;
  draftStatus?: "pending" | "approved";
}

function EditableRuleSection({
  title,
  icon,
  rules,
  onChange,
  editable,
}: {
  title: string;
  icon: React.ReactNode;
  rules: string[];
  onChange: (rules: string[]) => void;
  editable: boolean;
}) {
  const [open, setOpen] = useState(true);

  const updateRule = (index: number, value: string) => {
    const updated = [...rules];
    updated[index] = value;
    onChange(updated);
  };

  const removeRule = (index: number) => {
    onChange(rules.filter((_, i) => i !== index));
  };

  const addRule = () => {
    onChange([...rules, ""]);
  };

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
            <div key={i} className="flex items-start gap-1.5 group">
              <span className="text-deriv-teal mr-0.5 mt-2 text-sm shrink-0">+</span>
              {editable ? (
                <>
                  <input
                    type="text"
                    value={rule}
                    onChange={(e) => updateRule(i, e.target.value)}
                    className="flex-1 bg-white/5 border border-deriv-dark-border rounded px-2 py-1.5 text-sm text-deriv-grey focus:border-deriv-teal focus:outline-none focus:ring-1 focus:ring-deriv-teal/30 transition-colors"
                  />
                  <button
                    onClick={() => removeRule(i)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 text-deriv-red/60 hover:text-deriv-red transition-all shrink-0"
                    title="Remove rule"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </>
              ) : (
                <p className="text-sm text-deriv-grey leading-relaxed">{rule}</p>
              )}
            </div>
          ))}
          {editable && (
            <button
              onClick={addRule}
              className="flex items-center gap-1.5 text-xs text-deriv-teal/70 hover:text-deriv-teal transition-colors mt-2 ml-4"
            >
              <Plus className="w-3 h-3" />
              Add rule
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function DraftStatusBanner({
  status,
  onApprove,
  approving,
}: {
  status: "pending" | "approved";
  onApprove?: () => void;
  approving?: boolean;
}) {
  if (status === "approved") {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-deriv-teal/10 rounded-xl border border-deriv-teal/30 p-4"
      >
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-deriv-teal shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-bold text-deriv-teal">
              Approved & Live
            </p>
            <p className="text-xs text-deriv-grey mt-0.5">
              This rulebook has been approved and promoted to active. All future
              monitoring uses these updated rules.
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-deriv-amber/10 rounded-xl border border-deriv-amber/30 p-4"
    >
      <div className="flex items-start gap-3">
        <Clock className="w-5 h-5 text-deriv-amber shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-bold text-deriv-amber">
            Pending Review
          </p>
          <p className="text-xs text-deriv-grey mt-0.5 mb-3">
            Review and edit the proposed rulebook below, then approve to go live.
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={onApprove}
              disabled={approving}
              className={cn(
                "flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-colors",
                "bg-deriv-teal text-white hover:bg-deriv-teal/90",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {approving ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Check className="w-3.5 h-3.5" />
              )}
              {approving ? "Approving..." : "Approve & Go Live"}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function ComplianceAgentOutput({
  result,
  onApprove,
  approving,
  draftStatus,
}: ComplianceAgentOutputProps) {
  const [showUpdatedRulebook, setShowUpdatedRulebook] = useState(true);
  const [editedRulebook, setEditedRulebook] = useState<Rulebook>(
    () => structuredClone(result.updated_rulebook)
  );

  const effectiveStatus = draftStatus ?? (result.status === "pending_review" ? "pending" : "approved");
  const hasDraft = !!result.draft_id;
  const isPending = effectiveStatus === "pending";

  const handleApprove = () => {
    onApprove?.(editedRulebook);
  };

  const updateRiskScoreRule = (index: number, field: keyof RuleEntry, value: string | number) => {
    const updated = structuredClone(editedRulebook);
    if (updated.risk_score?.rules) {
      (updated.risk_score.rules[index] as unknown as Record<string, unknown>)[field] = value;
      setEditedRulebook(updated);
    }
  };

  const removeRiskScoreRule = (index: number) => {
    const updated = structuredClone(editedRulebook);
    if (updated.risk_score?.rules) {
      updated.risk_score.rules = updated.risk_score.rules.filter((_, i) => i !== index);
      setEditedRulebook(updated);
    }
  };

  const addRiskScoreRule = () => {
    const updated = structuredClone(editedRulebook);
    if (updated.risk_score?.rules) {
      updated.risk_score.rules.push({ category: "", rule: "", points: 0 });
      setEditedRulebook(updated);
    }
  };

  const updateRiskBand = (band: string, value: string) => {
    const updated = structuredClone(editedRulebook);
    if (updated.risk_bands) {
      updated.risk_bands[band] = value;
      setEditedRulebook(updated);
    }
  };

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

      {hasDraft && (
        <DraftStatusBanner
          status={effectiveStatus as "pending" | "approved"}
          onApprove={handleApprove}
          approving={approving}
        />
      )}

      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <h4 className="text-sm font-semibold text-white mb-3">Agent Chain</h4>
        <AgentChainLog chain={result.agent_chain} />
      </div>

      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-5 h-5 text-deriv-teal" />
          <h4 className="text-sm font-semibold text-white">Summary</h4>
        </div>
        <p className="text-sm text-deriv-grey leading-relaxed">
          {result.summary}
        </p>
      </div>

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

      <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-5 h-5 text-deriv-red" />
          <h4 className="text-sm font-semibold text-white">Impact Analysis</h4>
        </div>
        <p className="text-sm text-deriv-grey leading-relaxed">
          {result.impact_analysis}
        </p>
      </div>

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

      {result.updated_rulebook && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={cn(
            "bg-deriv-dark-card rounded-xl border overflow-hidden",
            isPending
              ? "border-deriv-amber/30"
              : "border-deriv-teal/30"
          )}
        >
          <button
            onClick={() => setShowUpdatedRulebook(!showUpdatedRulebook)}
            className="w-full px-5 py-4 flex items-center justify-between border-b border-deriv-teal/20 hover:bg-deriv-teal/5 transition-colors"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-deriv-teal" />
              <h4 className="text-sm font-bold text-white">
                {isPending ? "Proposed" : "Updated"} Rulebook — {result.new_version}
              </h4>
              <span
                className={cn(
                  "inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                  isPending
                    ? "bg-deriv-amber/20 text-deriv-amber"
                    : "bg-deriv-teal/20 text-deriv-teal"
                )}
              >
                {isPending ? "Editable Draft" : "Active"}
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
              {isPending && (
                <div className="px-5 py-2.5 bg-deriv-amber/5 border-b border-deriv-amber/20">
                  <p className="text-xs text-deriv-amber flex items-center gap-1.5">
                    <Pencil className="w-3 h-3" />
                    Click any rule to edit. Add or remove rules before approving.
                  </p>
                </div>
              )}

              <EditableRuleSection
                title="Amount-Based Rules"
                icon={<DollarSign className="w-4 h-4 text-deriv-amber shrink-0" />}
                rules={editedRulebook.amount_based}
                editable={isPending}
                onChange={(rules) =>
                  setEditedRulebook({ ...editedRulebook, amount_based: rules })
                }
              />
              <EditableRuleSection
                title="Frequency-Based Rules"
                icon={<Repeat className="w-4 h-4 text-deriv-teal shrink-0" />}
                rules={editedRulebook.frequency_based}
                editable={isPending}
                onChange={(rules) =>
                  setEditedRulebook({ ...editedRulebook, frequency_based: rules })
                }
              />
              <EditableRuleSection
                title="Location-Based Rules"
                icon={<MapPin className="w-4 h-4 text-deriv-red shrink-0" />}
                rules={editedRulebook.location_based}
                editable={isPending}
                onChange={(rules) =>
                  setEditedRulebook({ ...editedRulebook, location_based: rules })
                }
              />
              <EditableRuleSection
                title="Behavioural Pattern Rules"
                icon={<Brain className="w-4 h-4 text-purple-400 shrink-0" />}
                rules={editedRulebook.behavioural_pattern}
                editable={isPending}
                onChange={(rules) =>
                  setEditedRulebook({ ...editedRulebook, behavioural_pattern: rules })
                }
              />

              {editedRulebook.risk_score?.rules && (
                <div className="px-4 py-3 border-b border-deriv-teal/20">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4 text-deriv-red shrink-0" />
                    <span className="text-sm font-semibold text-white">
                      Risk Scoring ({editedRulebook.risk_score.range})
                    </span>
                  </div>
                  <table className="w-full text-sm ml-6">
                    <thead>
                      <tr className="text-deriv-grey text-left">
                        <th className="pb-2 font-medium">Category</th>
                        <th className="pb-2 font-medium">Rule</th>
                        <th className="pb-2 font-medium text-right">Points</th>
                        {isPending && <th className="pb-2 w-8"></th>}
                      </tr>
                    </thead>
                    <tbody>
                      {editedRulebook.risk_score.rules.map(
                        (rule: RuleEntry, i: number) => (
                          <tr
                            key={i}
                            className="border-t border-deriv-dark-border/50 group"
                          >
                            <td className="py-2">
                              {isPending ? (
                                <input
                                  type="text"
                                  value={rule.category}
                                  onChange={(e) => updateRiskScoreRule(i, "category", e.target.value)}
                                  className="w-full bg-white/5 border border-deriv-dark-border rounded px-2 py-1 text-sm text-deriv-amber font-medium focus:border-deriv-teal focus:outline-none focus:ring-1 focus:ring-deriv-teal/30"
                                />
                              ) : (
                                <span className="text-deriv-amber font-medium">{rule.category}</span>
                              )}
                            </td>
                            <td className="py-2">
                              {isPending ? (
                                <input
                                  type="text"
                                  value={rule.rule}
                                  onChange={(e) => updateRiskScoreRule(i, "rule", e.target.value)}
                                  className="w-full bg-white/5 border border-deriv-dark-border rounded px-2 py-1 text-sm text-deriv-grey focus:border-deriv-teal focus:outline-none focus:ring-1 focus:ring-deriv-teal/30"
                                />
                              ) : (
                                <span className="text-deriv-grey">{rule.rule}</span>
                              )}
                            </td>
                            <td className="py-2 text-right">
                              {isPending ? (
                                <input
                                  type="number"
                                  value={rule.points}
                                  onChange={(e) => updateRiskScoreRule(i, "points", parseInt(e.target.value) || 0)}
                                  className="w-16 bg-white/5 border border-deriv-dark-border rounded px-2 py-1 text-sm text-deriv-red font-bold text-right focus:border-deriv-teal focus:outline-none focus:ring-1 focus:ring-deriv-teal/30"
                                />
                              ) : (
                                <span className="text-deriv-red font-bold">+{rule.points}</span>
                              )}
                            </td>
                            {isPending && (
                              <td className="py-2 pl-1">
                                <button
                                  onClick={() => removeRiskScoreRule(i)}
                                  className="opacity-0 group-hover:opacity-100 p-1 text-deriv-red/60 hover:text-deriv-red transition-all"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            )}
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                  {isPending && (
                    <button
                      onClick={addRiskScoreRule}
                      className="flex items-center gap-1.5 text-xs text-deriv-teal/70 hover:text-deriv-teal transition-colors mt-2 ml-6"
                    >
                      <Plus className="w-3 h-3" />
                      Add scoring rule
                    </button>
                  )}
                </div>
              )}

              {editedRulebook.risk_bands && (
                <div className="px-4 py-3">
                  <div className="ml-6 space-y-1.5">
                    <p className="text-xs text-deriv-grey uppercase font-semibold mb-2">
                      Risk Bands
                    </p>
                    {Object.entries(editedRulebook.risk_bands).map(
                      ([band, desc]) => (
                        <div
                          key={band}
                          className="flex items-center gap-2 text-sm"
                        >
                          <span
                            className={cn(
                              "w-2.5 h-2.5 rounded-full shrink-0",
                              band === "HIGH" && "bg-deriv-red",
                              band === "MEDIUM" && "bg-deriv-amber",
                              band === "LOW" && "bg-deriv-teal",
                              band === "CLEAN" && "bg-deriv-grey"
                            )}
                          />
                          <span className="text-white font-medium shrink-0">
                            {band}:
                          </span>
                          {isPending ? (
                            <input
                              type="text"
                              value={desc as string}
                              onChange={(e) => updateRiskBand(band, e.target.value)}
                              className="flex-1 bg-white/5 border border-deriv-dark-border rounded px-2 py-1 text-sm text-deriv-grey focus:border-deriv-teal focus:outline-none focus:ring-1 focus:ring-deriv-teal/30"
                            />
                          ) : (
                            <span className="text-deriv-grey">
                              {desc as string}
                            </span>
                          )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {isPending && showUpdatedRulebook && (
            <div className="px-5 py-3 bg-deriv-teal/5 border-t border-deriv-teal/20 flex items-center justify-end">
              <button
                onClick={handleApprove}
                disabled={approving}
                className={cn(
                  "flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-colors",
                  "bg-deriv-teal text-white hover:bg-deriv-teal/90",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                {approving ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Check className="w-3.5 h-3.5" />
                )}
                {approving ? "Approving..." : "Approve & Go Live"}
              </button>
            </div>
          )}
        </motion.div>
      )}

      {effectiveStatus === "approved" && (
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
                pattern analysis.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
