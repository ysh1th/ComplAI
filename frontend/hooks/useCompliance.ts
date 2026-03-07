"use client";

import { useState, useCallback, useRef } from "react";
import type { ComplianceData, CompliancePushResponse, Rulebook } from "@/lib/types";
import {
  getCompliance,
  pushCompliance,
  approveDraft as approveDraftApi,
} from "@/lib/api";

type DraftStatus = "pending" | "approved";

export function useCompliance() {
  const [dataCache, setDataCache] = useState<Record<string, ComplianceData>>({});
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [pushingId, setPushingId] = useState<string | null>(null);
  const [pushResultCache, setPushResultCache] = useState<Record<string, CompliancePushResponse>>({});
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);
  const [draftStatusCache, setDraftStatusCache] = useState<Record<string, DraftStatus>>({});
  const activeJurisdiction = useRef<string>("");

  const fetchCompliance = useCallback(async (jurisdictionCode: string) => {
    activeJurisdiction.current = jurisdictionCode;
    try {
      setLoading(true);
      const result = await getCompliance(jurisdictionCode);
      setDataCache((prev) => ({ ...prev, [jurisdictionCode]: result }));
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
        setDraftStatusCache((prev) => ({ ...prev, [jurisdictionCode]: "pending" }));
        const result = await pushCompliance(jurisdictionCode, regulationId);
        setPushResultCache((prev) => ({ ...prev, [jurisdictionCode]: result }));
        const refreshed = await getCompliance(jurisdictionCode);
        setDataCache((prev) => ({ ...prev, [jurisdictionCode]: refreshed }));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to push compliance");
      } finally {
        setPushing(false);
        setPushingId(null);
      }
    },
    []
  );

  const approveDraft = useCallback(
    async (jurisdictionCode: string, editedRulebook?: Rulebook) => {
      const pushResult = pushResultCache[jurisdictionCode];
      if (!pushResult?.draft_id) return;
      try {
        setApproving(true);
        setError(null);
        await approveDraftApi(pushResult.draft_id, editedRulebook);
        setDraftStatusCache((prev) => ({ ...prev, [jurisdictionCode]: "approved" }));
        const refreshed = await getCompliance(jurisdictionCode);
        setDataCache((prev) => ({ ...prev, [jurisdictionCode]: refreshed }));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to approve draft");
      } finally {
        setApproving(false);
      }
    },
    [pushResultCache]
  );

  const getDataForJurisdiction = useCallback(
    (jurisdictionCode: string) => dataCache[jurisdictionCode] ?? null,
    [dataCache]
  );

  const getPushResultForJurisdiction = useCallback(
    (jurisdictionCode: string) => pushResultCache[jurisdictionCode] ?? null,
    [pushResultCache]
  );

  const getDraftStatusForJurisdiction = useCallback(
    (jurisdictionCode: string): DraftStatus => draftStatusCache[jurisdictionCode] ?? "pending",
    [draftStatusCache]
  );

  return {
    loading,
    pushing,
    pushingId,
    error,
    approving,
    fetchCompliance,
    push,
    approveDraft,
    getData: getDataForJurisdiction,
    getPushResult: getPushResultForJurisdiction,
    getDraftStatus: getDraftStatusForJurisdiction,
  };
}
