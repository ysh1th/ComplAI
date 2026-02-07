"use client";

import { useState, useCallback } from "react";
import type { FullAnalysisResponse, IngestBatchRequest } from "@/lib/types";
import { ingestBatch } from "@/lib/api";

export function useInjectBatch() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FullAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const inject = useCallback(async (request: IngestBatchRequest) => {
    try {
      setLoading(true);
      setError(null);
      const data = await ingestBatch(request);
      setResult(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Injection failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    result,
    error,
    inject,
    clearResult: () => setResult(null),
  };
}
