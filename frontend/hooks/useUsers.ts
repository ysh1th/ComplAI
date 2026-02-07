"use client";

import { useState, useEffect, useCallback } from "react";
import type { UserWithState, FullAnalysisResponse } from "@/lib/types";
import { getInit } from "@/lib/api";

export function useUsers() {
  const [users, setUsers] = useState<UserWithState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getInit();
      setUsers(data.users);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const updateUserFromAnalysis = useCallback(
    (analysis: FullAnalysisResponse) => {
      setUsers((prev) =>
        prev.map((u) => {
          if (u.profile.user_id === analysis.user_id) {
            return {
              ...u,
              profile: {
                ...u.profile,
                risk_profile: analysis.risk_profile,
              },
              current_risk_score: analysis.risk_score,
              current_risk_band: analysis.risk_band,
              latest_analysis: analysis,
            };
          }
          return u;
        })
      );
    },
    []
  );

  // Sort by risk score descending
  const sortedUsers = [...users].sort(
    (a, b) => b.current_risk_score - a.current_risk_score
  );

  return {
    users: sortedUsers,
    loading,
    error,
    refetch: fetchUsers,
    updateUserFromAnalysis,
  };
}
