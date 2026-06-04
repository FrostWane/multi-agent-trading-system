import { useEffect, useMemo, useState } from "react";
import { Play, RefreshCw } from "lucide-react";
import { AgentTimeline } from "./components/AgentTimeline";
import { EvidencePanel } from "./components/EvidencePanel";
import { MetricGrid } from "./components/MetricGrid";
import { PriceChart } from "./components/PriceChart";
import { ReportPanel } from "./components/ReportPanel";
import { eventsUrl, fetchAnalysis, submitAnalysis } from "./lib/api";
import type { AgentEvent, AnalysisSnapshot, AnalyzeRequest } from "./types/analysis";

const defaultRequest: AnalyzeRequest = {
  symbol: "000001",
  start_date: "2024-01-01",
  end_date: "2024-12-31",
  horizon: "1m",
  risk_preference: "balanced"
};

export function App() {
  const [form, setForm] = useState<AnalyzeRequest>(defaultRequest);
  const [runId, setRunId] = useState<string>("");
  const [snapshot, setSnapshot] = useState<AnalysisSnapshot | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const result = snapshot?.result ?? null;
  const status = snapshot?.status ?? (loading ? "running" : "idle");
  const statusText: Record<string, string> = {
    idle: "待机",
    queued: "排队中",
    running: "分析中",
    completed: "已完成",
    failed: "失败"
  };

  const latestEvents = useMemo(() => {
    const byKey = new Map<string, AgentEvent>();
    [...events, ...(snapshot?.events ?? [])].forEach((event) => {
      byKey.set(`${event.agent}-${event.status}-${event.created_at}`, event);
    });
    return [...byKey.values()].sort((a, b) => a.created_at.localeCompare(b.created_at));
  }, [events, snapshot?.events]);

  useEffect(() => {
    if (!runId) return;
    const source = new EventSource(eventsUrl(runId));
    source.onmessage = (message) => {
      const event = JSON.parse(message.data) as AgentEvent;
      setEvents((current) => [...current, event]);
    };
    source.addEventListener("done", async () => {
      const next = await fetchAnalysis(runId);
      setSnapshot(next);
      setLoading(false);
      source.close();
    });
    source.onerror = () => {
      source.close();
    };
    return () => source.close();
  }, [runId]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setEvents([]);
    setSnapshot(null);
    try {
      const response = await submitAnalysis(form);
      setRunId(response.run_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
      setLoading(false);
    }
  }

  async function refresh() {
    if (!runId) return;
    setSnapshot(await fetchAnalysis(runId));
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>多智能体量化分析系统</h1>
          <p>A 股研究工作台</p>
        </div>
        <div className={`status-pill ${status}`}>{statusText[status] ?? status}</div>
      </header>

      <section className="workspace">
        <form className="control-panel" onSubmit={handleSubmit}>
          <label>
            股票代码
            <input
              value={form.symbol}
              maxLength={9}
              onChange={(event) => setForm({ ...form, symbol: event.target.value })}
            />
          </label>
          <label>
            开始日期
            <input
              type="date"
              value={form.start_date}
              onChange={(event) => setForm({ ...form, start_date: event.target.value })}
            />
          </label>
          <label>
            结束日期
            <input
              type="date"
              value={form.end_date}
              onChange={(event) => setForm({ ...form, end_date: event.target.value })}
            />
          </label>
          <label>
            分析周期
            <select value={form.horizon} onChange={(event) => setForm({ ...form, horizon: event.target.value })}>
              <option value="1w">1w</option>
              <option value="1m">1m</option>
              <option value="3m">3m</option>
            </select>
          </label>
          <label>
            风险偏好
            <select
              value={form.risk_preference}
              onChange={(event) =>
                setForm({ ...form, risk_preference: event.target.value as AnalyzeRequest["risk_preference"] })
              }
            >
              <option value="conservative">稳健</option>
              <option value="balanced">均衡</option>
              <option value="aggressive">进取</option>
            </select>
          </label>
          <div className="actions">
            <button type="submit" disabled={loading} title="开始分析">
              <Play size={17} aria-hidden="true" />
              分析
            </button>
            <button type="button" onClick={refresh} disabled={!runId} title="刷新结果">
              <RefreshCw size={17} aria-hidden="true" />
              刷新
            </button>
          </div>
          {error ? <p className="error">{error}</p> : null}
        </form>

        <MetricGrid result={result} />
        <AgentTimeline events={latestEvents} />
        <PriceChart data={result?.market_data_preview ?? []} />
        <EvidencePanel research={result?.research ?? []} />
        <ReportPanel result={result} />
      </section>
    </main>
  );
}
