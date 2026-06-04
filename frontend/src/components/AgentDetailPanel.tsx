import { Braces, Clock3 } from "lucide-react";
import type { AgentEvent } from "../types/analysis";

const AGENT_LABELS: Record<string, string> = {
  "Supervisor Agent": "调度智能体",
  "Market Data Agent": "行情数据智能体",
  "Quant Analyst Agent": "量化分析智能体",
  "RAG Research Agent": "RAG 研究智能体",
  "Risk Agent": "风险评估智能体",
  "Backtest Agent": "策略回测智能体",
  "Report Agent": "报告生成智能体",
  "Critic Agent": "结论校验智能体"
};

const STATUS_LABELS: Record<string, string> = {
  queued: "排队中",
  running: "执行中",
  completed: "已完成",
  failed: "失败"
};

function durationText(events: AgentEvent[]) {
  const running = events.find((event) => event.status === "running");
  const completed = [...events].reverse().find((event) => event.status === "completed" || event.status === "failed");
  if (!running || !completed) return "待计算";
  const diff = new Date(completed.created_at).getTime() - new Date(running.created_at).getTime();
  if (!Number.isFinite(diff) || diff < 0) return "待计算";
  return `${(diff / 1000).toFixed(2)} 秒`;
}

function prettyPayload(payload: Record<string, unknown> | undefined) {
  if (!payload || Object.keys(payload).length === 0) return "暂无结构化输出";
  return JSON.stringify(payload, null, 2);
}

export function AgentDetailPanel({
  events,
  selectedAgent
}: {
  events: AgentEvent[];
  selectedAgent: string;
}) {
  const agentEvents = events.filter((event) => event.agent === selectedAgent);
  const latest = agentEvents[agentEvents.length - 1];

  return (
    <section className="panel agent-detail-panel" aria-label="智能体详情">
      <div className="panel-heading">
        <h2>智能体详情</h2>
        <span>{AGENT_LABELS[selectedAgent] ?? selectedAgent}</span>
      </div>
      <div className="agent-detail-grid">
        <div className="detail-card">
          <Clock3 size={18} aria-hidden="true" />
          <span>耗时</span>
          <strong>{durationText(agentEvents)}</strong>
        </div>
        <div className="detail-card">
          <Braces size={18} aria-hidden="true" />
          <span>状态</span>
          <strong>{STATUS_LABELS[latest?.status ?? "queued"]}</strong>
        </div>
      </div>
      <div className="event-history">
        {agentEvents.length === 0 ? (
          <p className="empty">暂无事件。</p>
        ) : (
          agentEvents.map((event) => (
            <article key={`${event.created_at}-${event.status}`}>
              <span>{new Date(event.created_at).toLocaleTimeString()}</span>
              <strong>{event.message}</strong>
            </article>
          ))
        )}
      </div>
      <pre className="payload-view">{prettyPayload(latest?.payload)}</pre>
    </section>
  );
}
