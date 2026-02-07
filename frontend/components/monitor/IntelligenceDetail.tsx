"use client";

import type { UserWithState, IngestBatchRequest } from "@/lib/types";
import { RiskGauge } from "@/components/shared/RiskGauge";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { CountryFlag } from "@/components/shared/CountryFlag";
import { IdentityCard } from "./IdentityCard";
import { BehavioralAnalysis } from "./BehavioralAnalysis";
import { AIGuardian } from "./AIGuardian";
import { DataInjectionFlow } from "./DataInjectionFlow";
import { getJurisdictionName } from "@/lib/utils";
import { Shield, Eye } from "lucide-react";

interface IntelligenceDetailProps {
  user: UserWithState;
  allUsers: UserWithState[];
  injecting: boolean;
  onInject: (request: IngestBatchRequest) => Promise<void>;
}

export function IntelligenceDetail({
  user,
  allUsers,
  injecting,
  onInject,
}: IntelligenceDetailProps) {
  const analysis = user.latest_analysis;

  return (
    <div className="h-full overflow-y-auto p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-bold text-white">
              {user.profile.full_name}
            </h2>
            <CountryFlag code={user.profile.country} size="lg" />
          </div>
          <div className="flex items-center gap-2 text-sm text-deriv-grey">
            <Shield className="w-4 h-4" />
            <span>{getJurisdictionName(user.profile.country)}</span>
            <span>•</span>
            <span>{user.profile.user_id}</span>
            <span>•</span>
            <RiskBadge band={user.current_risk_band} size="md" />
          </div>
        </div>
        <RiskGauge
          score={user.current_risk_score}
          band={user.current_risk_band}
          size={140}
        />
      </div>

      {/* Identity */}
      <IdentityCard profile={user.profile} baseline={user.baseline} />

      {/* Data Injection — embedded in detail panel */}
      <DataInjectionFlow
        user={user}
        allUsers={allUsers}
        loading={injecting}
        onInject={onInject}
      />

      {/* Behavioral Analysis (only if we have analysis data) */}
      {analysis && (
        <BehavioralAnalysis
          baseline={analysis.baseline}
          preprocessed={analysis.preprocessed}
        />
      )}

      {/* AI Guardian (only if we have analysis data) */}
      {analysis ? (
        <AIGuardian analysis={analysis} />
      ) : (
        <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-8 text-center">
          <Eye className="w-10 h-10 text-deriv-grey mx-auto mb-3 opacity-50" />
          <p className="text-base text-deriv-grey">
            No analysis data yet. Inject a transaction batch to trigger the AI agents.
          </p>
        </div>
      )}
    </div>
  );
}
