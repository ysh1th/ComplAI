"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Wrench, Shield, ChevronDown, ChevronRight } from "lucide-react";
import type { AgentLogEntry } from "@/lib/types";
import { getStatusColor } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface AgentChainLogProps {
  chain: AgentLogEntry[];
}

function RetryBadge({
  count,
  type,
  onClick,
}: {
  count: number;
  type?: "technical" | "logical" | null;
  onClick?: () => void;
}) {
  if (!count || count === 0) return null;

  const isTechnical = type === "technical";
  const bgColor = isTechnical
    ? "bg-deriv-amber/20 border-deriv-amber/40 text-deriv-amber"
    : "bg-purple-500/20 border-purple-500/40 text-purple-400";
  const label = isTechnical ? "Technical Fix" : "Logic Review";

  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[10px] font-bold",
        "cursor-pointer hover:opacity-80 transition-opacity",
        bgColor
      )}
      title={`${count} ${isTechnical ? "technical" : "logical"} retry(s) — click for details`}
    >
      {isTechnical ? (
        <Wrench className="w-2.5 h-2.5" />
      ) : (
        <Shield className="w-2.5 h-2.5" />
      )}
      <span>x{count + 1}</span>
      <span className="hidden sm:inline ml-0.5">{label}</span>
    </button>
  );
}

function AgentStepEntry({
  entry,
  index,
  isLast,
}: {
  entry: AgentLogEntry;
  index: number;
  isLast: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasRetries = (entry.retry_count ?? 0) > 0;
  const retryCount = entry.retry_count ?? 0;

  const statusColor = getStatusColor(entry.status);

  const pulseClass = hasRetries
    ? entry.status === "error"
      ? "animate-pulse-red"
      : "animate-pulse-green"
    : "";

  return (
    <motion.div
      key={`${entry.agent}-${index}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.15, duration: 0.3 }}
      className="flex items-start gap-3 relative"
    >
      {!isLast && (
        <div
          className="absolute left-[17px] top-[36px] w-[2px] h-[calc(100%-8px)]"
          style={{ backgroundColor: statusColor + "30" }}
        />
      )}

      <div
        className={cn(
          "w-[34px] h-[34px] rounded-full flex items-center justify-center text-base shrink-0 mt-1",
          pulseClass
        )}
        style={{
          backgroundColor: statusColor + "15",
          border: `1.5px solid ${statusColor}40`,
        }}
      >
        {entry.icon}
      </div>

      <div className="flex-1 pb-4 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-semibold text-white">
            {entry.agent}
          </span>

          {hasRetries && (
            <RetryBadge
              count={retryCount}
              type={entry.retry_type}
              onClick={() => setExpanded(!expanded)}
            />
          )}

          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: statusColor }}
          />
          <span className="text-xs text-deriv-grey">
            {entry.duration_ms}ms
          </span>
        </div>

        <p className="text-sm text-deriv-grey mt-0.5 leading-relaxed break-words">
          {entry.message}
        </p>

        <AnimatePresence>
          {hasRetries && expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-2 ml-1 pl-3 border-l-2 border-deriv-dark-border space-y-1.5">
                <p className="text-[11px] font-semibold text-deriv-grey uppercase tracking-wider">
                  Refinement History
                </p>
                {Array.from({ length: retryCount }).map((_, attemptIdx) => (
                  <div
                    key={attemptIdx}
                    className="flex items-start gap-2 text-xs text-deriv-grey"
                  >
                    <span
                      className={cn(
                        "shrink-0 px-1.5 py-0.5 rounded text-[10px] font-bold",
                        "bg-deriv-red/15 text-deriv-red border border-deriv-red/30"
                      )}
                    >
                      Attempt {attemptIdx + 1}
                    </span>
                    <span>
                      {entry.retry_type === "logical"
                        ? "Failed logic check — Validator requested re-evaluation"
                        : "Failed structural validation — Pydantic guardrail triggered retry"}
                    </span>
                  </div>
                ))}
                <div className="flex items-start gap-2 text-xs text-deriv-grey">
                  <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-bold bg-deriv-teal/15 text-deriv-teal border border-deriv-teal/30">
                    Attempt {retryCount + 1}
                  </span>
                  <span>Passed all guardrails — Self-corrected output accepted</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export function AgentChainLog({ chain }: AgentChainLogProps) {
  return (
    <div className="space-y-0">
      {chain.map((entry, index) => (
        <AgentStepEntry
          key={`${entry.agent}-${index}`}
          entry={entry}
          index={index}
          isLast={index === chain.length - 1}
        />
      ))}
    </div>
  );
}
