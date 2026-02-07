import type {
  InitResponse,
  FullAnalysisResponse,
  ComplianceData,
  CompliancePushResponse,
  IngestBatchRequest,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }

  return response.json();
}

export async function getInit(): Promise<InitResponse> {
  return fetchApi<InitResponse>("/api/init");
}

export async function getCompliance(jurisdictionCode: string): Promise<ComplianceData> {
  return fetchApi<ComplianceData>(`/api/compliance/${jurisdictionCode}`);
}

export async function getRules(jurisdictionCode: string) {
  return fetchApi<{ jurisdiction: string; current_version: string; rulebook: any }>(
    `/api/rules/${jurisdictionCode}`
  );
}

export async function ingestBatch(
  request: IngestBatchRequest
): Promise<FullAnalysisResponse> {
  return fetchApi<FullAnalysisResponse>("/api/ingest-batch", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function pushCompliance(
  jurisdictionCode: string,
  regulationUpdateId: string
): Promise<CompliancePushResponse> {
  return fetchApi<CompliancePushResponse>(
    `/api/compliance/${jurisdictionCode}/push`,
    {
      method: "POST",
      body: JSON.stringify({ regulation_update_id: regulationUpdateId }),
    }
  );
}
