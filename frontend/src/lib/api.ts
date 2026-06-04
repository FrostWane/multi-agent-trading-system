import type { AnalysisSnapshot, AnalyzeRequest, RagIngestPayload, StockOption } from "../types/analysis";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function submitAnalysis(payload: AnalyzeRequest): Promise<{ run_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`分析请求失败：${response.status}`);
  }
  return response.json();
}

export async function fetchAnalysis(runId: string): Promise<AnalysisSnapshot> {
  const response = await fetch(`${API_BASE}/api/analysis/${runId}`);
  if (!response.ok) {
    throw new Error(`结果查询失败：${response.status}`);
  }
  return response.json();
}

export async function searchStocks(query: string): Promise<StockOption[]> {
  const response = await fetch(`${API_BASE}/api/stocks/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`股票搜索失败：${response.status}`);
  }
  const data = (await response.json()) as { items: StockOption[] };
  return data.items;
}

export async function ingestRagDocument(payload: RagIngestPayload): Promise<{ status: string; count: number }> {
  const response = await fetch(`${API_BASE}/api/rag/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`文档导入失败：${response.status}`);
  }
  return response.json();
}

export function eventsUrl(runId: string): string {
  return `${API_BASE}/api/analysis/${runId}/events`;
}
