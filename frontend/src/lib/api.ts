import type { AnalysisSnapshot, AnalyzeRequest } from "../types/analysis";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function submitAnalysis(payload: AnalyzeRequest): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`Analysis request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchAnalysis(runId: string): Promise<AnalysisSnapshot> {
  const response = await fetch(`${API_BASE}/api/analysis/${runId}`);
  if (!response.ok) {
    throw new Error(`Snapshot request failed: ${response.status}`);
  }
  return response.json();
}

export function eventsUrl(runId: string): string {
  return `${API_BASE}/api/analysis/${runId}/events`;
}
