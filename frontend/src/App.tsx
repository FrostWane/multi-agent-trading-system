import { useEffect, useMemo, useState } from "react";
import { BarChart3, Bot, FileText, Play, RefreshCw } from "lucide-react";
import { AgentDetailPanel } from "./components/AgentDetailPanel";
import { AgentTimeline } from "./components/AgentTimeline";
import { BacktestPanel } from "./components/BacktestPanel";
import { EvidencePanel } from "./components/EvidencePanel";
import { MetricGrid } from "./components/MetricGrid";
import { PriceChart } from "./components/PriceChart";
import { RagIngestPanel } from "./components/RagIngestPanel";
import { ReportPanel } from "./components/ReportPanel";
import { StockSearch } from "./components/StockSearch";
import { eventsUrl, fetchAnalysis, submitAnalysis } from "./lib/api";
import type { AgentEvent, AnalysisSnapshot, AnalyzeRequest } from "./types/analysis";

type WorkbenchView = "market" | "agents" | "report";

const SESSION_STORAGE_KEY = "multi-agent-trading-system:last-session";

const defaultRequest: AnalyzeRequest = {
  symbol: "000001",
  start_date: "2026-01-01",
  end_date: formatLocalDate(new Date()),
  horizon: "1m",
  risk_preference: "balanced",
  backtest_config: {
    strategy_set: "compare_all",
    short_window: 5,
    long_window: 20,
    momentum_window: 20,
    rsi_window: 14,
    rsi_buy_threshold: 30,
    rsi_sell_threshold: 70,
    initial_cash: 100000,
    fee_rate: 0.0003
  }
};

function formatLocalDate(value: Date) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

interface PersistedSession {
  activeView?: WorkbenchView;
  events?: AgentEvent[];
  form?: AnalyzeRequest;
  runId?: string;
  selectedAgent?: string;
  snapshot?: AnalysisSnapshot | null;
}

function isWorkbenchView(value: unknown): value is WorkbenchView {
  return value === "market" || value === "agents" || value === "report";
}

function isActiveStatus(status: AnalysisSnapshot["status"] | undefined) {
  return status === "queued" || status === "running";
}

function readPersistedSession(): PersistedSession {
  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as PersistedSession;
    return {
      activeView: isWorkbenchView(parsed.activeView) ? parsed.activeView : undefined,
      events: Array.isArray(parsed.events) ? parsed.events : undefined,
      form: parsed.form?.symbol ? parsed.form : undefined,
      runId: typeof parsed.runId === "string" ? parsed.runId : undefined,
      selectedAgent: typeof parsed.selectedAgent === "string" ? parsed.selectedAgent : undefined,
      snapshot: parsed.snapshot ?? null
    };
  } catch {
    return {};
  }
}

function writePersistedSession(session: PersistedSession) {
  try {
    window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  } catch {
    // localStorage can be unavailable in private mode or full quota; analysis still works in memory.
  }
}

export function App() {
  const persistedSession = useMemo(readPersistedSession, []);
  const [form, setForm] = useState<AnalyzeRequest>(() => persistedSession.form ?? defaultRequest);
  const [runId, setRunId] = useState<string>(() => persistedSession.runId ?? "");
  const [snapshot, setSnapshot] = useState<AnalysisSnapshot | null>(() => persistedSession.snapshot ?? null);
  const [events, setEvents] = useState<AgentEvent[]>(() => persistedSession.events ?? []);
  const [selectedAgent, setSelectedAgent] = useState(() => persistedSession.selectedAgent ?? "Supervisor Agent");
  const [activeView, setActiveView] = useState<WorkbenchView>(() => persistedSession.activeView ?? "market");
  const [loading, setLoading] = useState(() => isActiveStatus(persistedSession.snapshot?.status));
  const [error, setError] = useState("");

  const result = snapshot?.result ?? null;
  const status = snapshot?.status ?? (loading ? "running" : "idle");
  const strategies = Array.isArray(result?.backtest?.strategies) ? result.backtest.strategies : [];
  const researchItems = Array.isArray(result?.research) ? result.research : [];
  const strategyCount = strategies.length;
  const citationCount = researchItems.length;
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
    writePersistedSession({
      activeView,
      events: latestEvents,
      form,
      runId,
      selectedAgent,
      snapshot
    });
  }, [activeView, form, latestEvents, runId, selectedAgent, snapshot]);

  useEffect(() => {
    if (!runId || snapshot) return;
    let cancelled = false;
    setLoading(true);
    fetchAnalysis(runId)
      .then((next) => {
        if (cancelled) return;
        setSnapshot(next);
        setForm(next.request);
        setLoading(isActiveStatus(next.status));
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "恢复上次分析失败");
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [runId, snapshot]);

  useEffect(() => {
    if (!runId) return;
    const source = new EventSource(eventsUrl(runId));
    source.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data) as AgentEvent;
        setEvents((current) => [...current, event]);
      } catch {
        setError("Agent 事件解析失败，已保留当前结果");
      }
    };
    source.addEventListener("done", async () => {
      try {
        const next = await fetchAnalysis(runId);
        setSnapshot(next);
        setForm(next.request);
      } catch (err) {
        setError(err instanceof Error ? err.message : "结果刷新失败");
      } finally {
        setLoading(false);
      }
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
    try {
      const next = await fetchAnalysis(runId);
      setSnapshot(next);
      setForm(next.request);
      setLoading(isActiveStatus(next.status));
    } catch (err) {
      setError(err instanceof Error ? err.message : "刷新失败");
    }
  }

  function updateBacktestConfig(key: keyof AnalyzeRequest["backtest_config"], value: string) {
    const numericKeys = new Set([
      "short_window",
      "long_window",
      "momentum_window",
      "rsi_window",
      "rsi_buy_threshold",
      "rsi_sell_threshold",
      "initial_cash",
      "fee_rate"
    ]);
    setForm((current) => ({
      ...current,
      backtest_config: {
        ...current.backtest_config,
        [key]: numericKeys.has(key) ? Number(value) : value
      }
    }));
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>多智能体量化分析系统</h1>
          <p>A 股研究、回测、证据检索与报告校验工作台</p>
        </div>
        <div className="topbar-meta">
          <span>{form.symbol}</span>
          <span>{form.start_date} 至 {form.end_date}</span>
          <div className={`status-pill ${status}`}>{statusText[status] ?? status}</div>
        </div>
      </header>

      <section className="dashboard-shell">
        <form className="control-panel" onSubmit={handleSubmit}>
          <div className="control-scroll">
            <div className="panel-heading compact-heading">
              <div>
                <h2>分析配置</h2>
                <p>选择标的、时间区间和策略参数</p>
              </div>
            </div>
            <StockSearch
              value={form.symbol}
              onSelect={(stock) => setForm((current) => ({ ...current, symbol: stock.symbol }))}
            />
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
            <div className="form-section">
              <h2>回测参数</h2>
              <label>
                策略范围
                <select
                  value={form.backtest_config.strategy_set}
                  onChange={(event) => updateBacktestConfig("strategy_set", event.target.value)}
                >
                  <option value="compare_all">多策略对比</option>
                  <option value="ma_cross">均线交叉</option>
                  <option value="momentum">动量策略</option>
                  <option value="rsi_reversal">RSI 反转</option>
                </select>
              </label>
              <div className="two-col compact">
                <label>
                  短均线
                  <input
                    type="number"
                    min={2}
                    max={120}
                    value={form.backtest_config.short_window}
                    onChange={(event) => updateBacktestConfig("short_window", event.target.value)}
                  />
                </label>
                <label>
                  长均线
                  <input
                    type="number"
                    min={3}
                    max={250}
                    value={form.backtest_config.long_window}
                    onChange={(event) => updateBacktestConfig("long_window", event.target.value)}
                  />
                </label>
              </div>
              <div className="two-col compact">
                <label>
                  动量窗口
                  <input
                    type="number"
                    min={2}
                    max={250}
                    value={form.backtest_config.momentum_window}
                    onChange={(event) => updateBacktestConfig("momentum_window", event.target.value)}
                  />
                </label>
                <label>
                  RSI 窗口
                  <input
                    type="number"
                    min={2}
                    max={120}
                    value={form.backtest_config.rsi_window}
                    onChange={(event) => updateBacktestConfig("rsi_window", event.target.value)}
                  />
                </label>
              </div>
              <div className="two-col compact">
                <label>
                  RSI 买入
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={form.backtest_config.rsi_buy_threshold}
                    onChange={(event) => updateBacktestConfig("rsi_buy_threshold", event.target.value)}
                  />
                </label>
                <label>
                  RSI 卖出
                  <input
                    type="number"
                    min={50}
                    max={99}
                    value={form.backtest_config.rsi_sell_threshold}
                    onChange={(event) => updateBacktestConfig("rsi_sell_threshold", event.target.value)}
                  />
                </label>
              </div>
              <label>
                初始资金
                <input
                  type="number"
                  min={1000}
                  step={1000}
                  value={form.backtest_config.initial_cash}
                  onChange={(event) => updateBacktestConfig("initial_cash", event.target.value)}
                />
              </label>
              <label>
                手续费率
                <input
                  type="number"
                  min={0}
                  max={0.02}
                  step={0.0001}
                  value={form.backtest_config.fee_rate}
                  onChange={(event) => updateBacktestConfig("fee_rate", event.target.value)}
                />
              </label>
            </div>
          </div>
          <div className="control-footer">
            <div className="run-context">
              <span>当前任务</span>
              <strong>{form.symbol} / {form.horizon} / {statusText[status] ?? status}</strong>
            </div>
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
          </div>
        </form>

        <section className="main-workbench">
          <MetricGrid result={result} />

          <nav className="view-tabs" aria-label="工作台视图">
            <button
              type="button"
              className={activeView === "market" ? "active" : ""}
              onClick={() => setActiveView("market")}
            >
              <BarChart3 size={17} aria-hidden="true" />
              行情回测
              <span>{strategyCount || "-"}</span>
            </button>
            <button
              type="button"
              className={activeView === "agents" ? "active" : ""}
              onClick={() => setActiveView("agents")}
            >
              <Bot size={17} aria-hidden="true" />
              智能体协作
              <span>{latestEvents.length}</span>
            </button>
            <button
              type="button"
              className={activeView === "report" ? "active" : ""}
              onClick={() => setActiveView("report")}
            >
              <FileText size={17} aria-hidden="true" />
              报告证据
              <span>{citationCount}</span>
            </button>
          </nav>

          <div className="tab-panel">
            {activeView === "market" ? (
              <div className="market-view">
                <PriceChart data={result?.market_data_preview ?? []} meta={result?.market_data_meta} />
                <BacktestPanel result={result} />
              </div>
            ) : null}

            {activeView === "agents" ? (
              <div className="agent-view">
                <AgentTimeline events={latestEvents} selectedAgent={selectedAgent} onSelectAgent={setSelectedAgent} />
                <AgentDetailPanel events={latestEvents} selectedAgent={selectedAgent} />
              </div>
            ) : null}

            {activeView === "report" ? (
              <div className="report-view">
                <ReportPanel result={result} />
                <div className="evidence-column">
                  <EvidencePanel research={researchItems} />
                  <RagIngestPanel symbol={form.symbol} />
                </div>
              </div>
            ) : null}
          </div>
        </section>
      </section>
    </main>
  );
}
