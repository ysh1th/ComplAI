"use client";

import type { UserProfile, UserBaseline } from "@/lib/types";
import { formatCurrency, getCountryName, INCOME_RANGES } from "@/lib/utils";
import {
  User,
  Briefcase,
  DollarSign,
  Globe,
  Shield,
  CheckCircle,
  AlertCircle,
  TrendingUp,
} from "lucide-react";

interface IdentityCardProps {
  profile: UserProfile;
  baseline: UserBaseline;
}

export function IdentityCard({ profile, baseline }: IdentityCardProps) {
  return (
    <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
      <h3 className="text-sm font-semibold text-deriv-grey uppercase tracking-wider mb-4">
        Identity & Profile
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <InfoItem
          icon={<User className="w-4 h-4" />}
          label="Age"
          value={`${profile.age} years`}
        />
        <InfoItem
          icon={<Briefcase className="w-4 h-4" />}
          label="Occupation"
          value={profile.occupation}
        />
        <InfoItem
          icon={<DollarSign className="w-4 h-4" />}
          label="Income"
          value={`${profile.income_level.charAt(0).toUpperCase() + profile.income_level.slice(1)} (${INCOME_RANGES[profile.income_level] ?? "N/A"})`}
        />
        <InfoItem
          icon={
            profile.kyc_status === "verified" ? (
              <CheckCircle className="w-4 h-4 text-deriv-teal" />
            ) : (
              <AlertCircle className="w-4 h-4 text-deriv-amber" />
            )
          }
          label="KYC"
          value={profile.kyc_status.charAt(0).toUpperCase() + profile.kyc_status.slice(1)}
        />
        <InfoItem
          icon={<Shield className="w-4 h-4" />}
          label="Risk Profile"
          value={profile.risk_profile.toUpperCase()}
        />
        <InfoItem
          icon={<TrendingUp className="w-4 h-4" />}
          label="Historical Trade Range"
          value={
            baseline.min_tx_amount_usd && baseline.max_tx_amount_usd
              ? `${formatCurrency(baseline.min_tx_amount_usd)} – ${formatCurrency(baseline.max_tx_amount_usd)}`
              : "N/A"
          }
        />
        <InfoItem
          icon={<DollarSign className="w-4 h-4" />}
          label="Avg Daily Volume"
          value={formatCurrency(baseline.avg_daily_total_usd)}
        />
        <div className="flex items-start gap-2.5 col-span-2">
          <Globe className="w-4 h-4 text-deriv-grey mt-0.5" />
          <div>
            <span className="text-xs text-deriv-grey block">
              Historical Countries
            </span>
            <span className="text-sm text-white font-medium">
              {profile.historical_countries
                .map((c) => getCountryName(c))
                .join(", ")}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-2.5">
      <span className="text-deriv-grey mt-0.5">{icon}</span>
      <div>
        <span className="text-xs text-deriv-grey block">{label}</span>
        <span className="text-sm text-white font-medium">{value}</span>
      </div>
    </div>
  );
}
