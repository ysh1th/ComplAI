"use client";

import { motion } from "framer-motion";
import type { UserWithState } from "@/lib/types";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { getInitials, getRiskColor, cn } from "@/lib/utils";

interface UserCardProps {
  user: UserWithState;
  selected: boolean;
  isNew?: boolean;
  onClick: () => void;
}

export function UserCard({ user, selected, isNew, onClick }: UserCardProps) {
  const color = getRiskColor(user.current_risk_band);

  return (
    <motion.div
      layout
      layoutId={user.profile.user_id}
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-3 py-3 rounded-xl cursor-pointer transition-colors",
        "border",
        selected
          ? "bg-deriv-red/5 border-deriv-red/30"
          : "border-transparent hover:bg-white/5",
        isNew && "animate-risk-pulse"
      )}
    >
      {/* Avatar */}
      <div
        className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0"
        style={{ backgroundColor: color + "30", color }}
      >
        {getInitials(user.profile.full_name)}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-base font-semibold text-white truncate">
            {user.profile.full_name}
          </span>
          <CountryFlag code={user.profile.country} size="sm" />
        </div>
        <span className="text-xs text-deriv-grey">
          {user.profile.user_id}
        </span>
      </div>

      {/* Risk */}
      <div className="flex flex-col items-end gap-1 shrink-0">
        <RiskBadge band={user.current_risk_band} size="sm" />
        <span
          className="text-sm font-bold"
          style={{ color }}
        >
          {user.current_risk_score}
        </span>
      </div>
    </motion.div>
  );
}
