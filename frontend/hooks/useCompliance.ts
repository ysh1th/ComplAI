"use client";

import { useState, useCallback, useRef } from "react";
import type { ComplianceData, CompliancePushResponse, Rulebook } from "@/lib/types";
import {
  getCompliance,
  pushCompliance,
  approveDraft as approveDraftApi,
} from "@/lib/api";

export function useCompliance() {
  const [data, setData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [pushingId, setPushingId] = useState<string | null>(null);
  const [pushResult, setPushResult] = useState<CompliancePushResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);
  const [draftStatus, setDraftStatus] = useState<"pending" | "approved">("pending");
  const preservePushResult = useRef(false);

  const fetchCompliance = useCallback(async (jurisdictionCode: string) => {
    try {
      setLoading(true);
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
        setDraftStatus("pending");
        const result = await pushCompliance(jurisdictionCode, regulationId);
        setPushResult(result);
        preservePushResult.current = true;
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

  const approveDraft = useCallback(
    async (jurisdictionCode: string, editedRulebook?: Rulebook) => {
      if (!pushResult?.draft_id) return;
      try {
        setApproving(true);
        setError(null);
        await approveDraftApi(pushResult.draft_id, editedRulebook);
        setDraftStatus("approved");
        preservePushResult.current = true;
        await fetchCompliance(jurisdictionCode);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to approve draft");
      } finally {
        setApproving(false);
      }
    },
    [pushResult, fetchCompliance]
  );

  return {
    data,
    loading,
    pushing,
    pushingId,
    pushResult,
    error,
    approving,
    draftStatus,
    fetchCompliance,
    push,
    approveDraft,
    clearPushResult: () => {
      setPushResult(null);
      setDraftStatus("pending");
    },
  };
}
