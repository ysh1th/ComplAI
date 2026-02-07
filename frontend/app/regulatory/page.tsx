"use client";

import { useState, useEffect, useRef } from "react";
import { useCompliance } from "@/hooks/useCompliance";
import { JurisdictionTabs } from "@/components/regulatory/JurisdictionTabs";
import { ComplianceSummary } from "@/components/regulatory/ComplianceSummary";
import { ActiveRulebook } from "@/components/regulatory/ActiveRulebook";
import { PushCompliance } from "@/components/regulatory/PushCompliance";
import { ComplianceAgentOutput } from "@/components/regulatory/ComplianceAgentOutput";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { BookOpen } from "lucide-react";

export default function RegulatoryPage() {
  const [activeTab, setActiveTab] = useState("AE");
  const { data, loading, pushing, pushingId, pushResult, error, fetchCompliance, push, clearPushResult } =
    useCompliance();
  const rulebookRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchCompliance(activeTab);
  }, [activeTab, fetchCompliance]);

  // Clear pushResult when switching tabs
  useEffect(() => {
    clearPushResult();
  }, [activeTab]); // eslint-disable-line react-hooks/exhaustive-deps

  // Scroll to the active rulebook after a push completes
  useEffect(() => {
    if (pushResult && rulebookRef.current) {
      // Small delay to let the DOM update first
      const timer = setTimeout(() => {
        rulebookRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [pushResult]);

  const handlePush = (regulationId: string) => {
    push(activeTab, regulationId);
  };

  const rulebookWasUpdated = !!pushResult;

  return (
    <div className="h-full overflow-y-auto relative">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-deriv-dark-border bg-deriv-dark-card/50 backdrop-blur-sm">
        <BookOpen className="w-6 h-6 text-deriv-red" />
        <h1 className="text-xl font-bold text-white">Regulatory Hub</h1>
        <span className="text-sm text-deriv-grey ml-2">
          Agentic compliance intelligence across jurisdictions
        </span>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto p-6 space-y-6">
        {/* Jurisdiction Tabs */}
        <JurisdictionTabs active={activeTab} onSelect={setActiveTab} />

        {/* Loading */}
        {loading && <LoadingSpinner text="Loading compliance data..." />}

        {/* Error */}
        {error && (
          <div className="bg-deriv-red/10 border border-deriv-red/20 rounded-xl p-4 text-sm text-deriv-red">
            {error}
          </div>
        )}

        {/* Content */}
        {data && !loading && (
          <div className="space-y-6">
            {/* Compliance Summary */}
            <ComplianceSummary data={data} />

            {/* Active Rulebook — scroll target */}
            <div ref={rulebookRef}>
              <ActiveRulebook
                rulebook={data.rulebook}
                version={data.current_version}
                isUpdated={rulebookWasUpdated}
              />
            </div>

            {/* Push New Compliance */}
            <PushCompliance
              regulations={data.available_new_regulations}
              pushing={pushing}
              pushingId={pushingId}
              onPush={handlePush}
            />

            {/* Pushing indicator */}
            {pushing && (
              <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-6">
                <LoadingSpinner text="Compliance agents working... Summarizing → Comparing → Analyzing → Editing Rulebook" />
              </div>
            )}
          </div>
        )}

        {/* Push Result - rendered outside loading gate so it persists after refetch */}
        {pushResult && <ComplianceAgentOutput result={pushResult} />}
      </div>
    </div>
  );
}
