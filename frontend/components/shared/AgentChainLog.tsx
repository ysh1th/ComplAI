"use client";

import { motion } from "framer-motion";
import type { AgentLogEntry } from "@/lib/types";
import { getStatusColor } from "@/lib/utils";

interface AgentChainLogProps {
  chain: AgentLogEntry[];
}

export function AgentChainLog({ chain }: AgentChainLogProps) {
  return (
    <div className="space-y-0">
      {chain.map((entry, index) => (
        <motion.div
          key={`${entry.agent}-${index}`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.15, duration: 0.3 }}
          className="flex items-start gap-3 relative"
        >
          {/* Timeline line */}
          {index < chain.length - 1 && (
            <div
              className="absolute left-[17px] top-[36px] w-[2px] h-[calc(100%-8px)]"
              style={{ backgroundColor: getStatusColor(entry.status) + "30" }}
            />
          )}

          {/* Icon */}
          <div
            className="w-[34px] h-[34px] rounded-full flex items-center justify-center text-base shrink-0 mt-1"
            style={{
              backgroundColor: getStatusColor(entry.status) + "15",
              border: `1.5px solid ${getStatusColor(entry.status)}40`,
            }}
          >
            {entry.icon}
          </div>

          {/* Content */}
          <div className="flex-1 pb-4 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-white">
                {entry.agent}
              </span>
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: getStatusColor(entry.status) }}
              />
              <span className="text-xs text-deriv-grey">
                {entry.duration_ms}ms
              </span>
            </div>
            <p className="text-sm text-deriv-grey mt-0.5 leading-relaxed break-words">
              {entry.message}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
