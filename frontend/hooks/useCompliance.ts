"use client";

import { useState, useCallback, useRef } from "react";
import type { ComplianceData, CompliancePushResponse } from "@/lib/types";
import { getCompliance, pushCompliance } from "@/lib/api";

export function useCompliance() {
  const [data, setData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [pushingId, setPushingId] = useState<string | null>(null);
  const [pushResult, setPushResult] = useState<CompliancePushResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const preservePushResult = useRef(false);

  const fetchCompliance = useCallback(async (jurisdictionCode: string) => {
    try {
      setLoading(true);
      // Only clear pushResult on normal fetches, not after a push
      if (!preservePushResult.current) {
        setPushResult(null);
      }
      preservePushResult.current = false;
      const result = await getCompliance(jurisdictionCode);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load compliance");
    } finally {
      setLoading(false);
    }
  }, []);

  const push = useCallback(
    async (jurisdictionCode: string, regulationId: string) => {
      try {
        setPushing(true);
        setPushingId(regulationId);
        setError(null);
        const result = await pushCompliance(jurisdictionCode, regulationId);
        setPushResult(result);
        // Preserve pushResult during the post-push refetch
        preservePushResult.current = true;
        // Refetch compliance data to get updated state
        await fetchCompliance(jurisdictionCode);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to push compliance");
      } finally {
        setPushing(false);
        setPushingId(null);
      }
    },
    [fetchCompliance]
  );

  return {
    data,
    loading,
    pushing,
    pushingId,
    pushResult,
    error,
    fetchCompliance,
    push,
    clearPushResult: () => setPushResult(null),
  };
}
