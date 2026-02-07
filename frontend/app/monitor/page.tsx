"use client";

import { useState, useCallback } from "react";
import { useUsers } from "@/hooks/useUsers";
import { useInjectBatch } from "@/hooks/useInjectBatch";
import { UserRoster } from "@/components/monitor/UserRoster";
import { IntelligenceDetail } from "@/components/monitor/IntelligenceDetail";
import type { IngestBatchRequest } from "@/lib/types";
import { Activity } from "lucide-react";

export default function MonitorPage() {
  const { users, loading, updateUserFromAnalysis } = useUsers();
  const { loading: injecting, inject } = useInjectBatch();
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [recentlyUpdatedId, setRecentlyUpdatedId] = useState<string | null>(null);

  const selectedUser = users.find(
    (u) => u.profile.user_id === selectedUserId
  );

  const handleInject = useCallback(
    async (request: IngestBatchRequest) => {
      try {
        const result = await inject(request);
        if (result) {
          updateUserFromAnalysis(result);
          setSelectedUserId(result.user_id);
          setRecentlyUpdatedId(result.user_id);
          setTimeout(() => setRecentlyUpdatedId(null), 2500);
        }
      } catch {
        // Error handled by hook
      }
    },
    [inject, updateUserFromAnalysis]
  );

  return (
    <div className="h-full flex flex-col relative">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-deriv-dark-border bg-deriv-dark-card/50">
        <Activity className="w-6 h-6 text-deriv-red" />
        <h1 className="text-xl font-bold text-white">Live Monitor</h1>
        <span className="text-sm text-deriv-grey ml-2">
          AI-powered behavioral anomaly detection
        </span>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: User Roster (35%) */}
        <div className="w-[35%] min-w-[280px] max-w-[400px] border-r border-deriv-dark-border bg-deriv-dark-card/30">
          <UserRoster
            users={users}
            selectedUserId={selectedUserId}
            onSelectUser={setSelectedUserId}
            loading={loading}
            recentlyUpdatedId={recentlyUpdatedId}
          />
        </div>

        {/* Right: Intelligence Detail (65%) */}
        <div className="flex-1 bg-deriv-black/50">
          {selectedUser ? (
            <IntelligenceDetail
              user={selectedUser}
              allUsers={users}
              injecting={injecting}
              onInject={handleInject}
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Activity className="w-12 h-12 text-deriv-grey/30 mx-auto mb-4" />
                <p className="text-base text-deriv-grey">
                  Select a user from the roster to view their intelligence profile
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
