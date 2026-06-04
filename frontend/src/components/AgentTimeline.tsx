import { CheckCircle2, CircleDot, Loader2, XCircle } from "lucide-react";
import type { AgentEvent } from "../types/analysis";

const AGENTS = [
  "Supervisor Agent",
  "Market Data Agent",
  "Quant Analyst Agent",
  "RAG Research Agent",
  "Risk Agent",
  "Backtest Agent",
  "Report Agent",
  "Critic Agent"
];

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

function latestByAgent(events: AgentEvent[]) {
  return AGENTS.map((agent) => {
    const latest = [...events].reverse().find((event) => event.agent === agent);
    return { agent, event: latest };
  });
}

export function AgentTimeline({
  events,
  selectedAgent,
  onSelectAgent
}: {
  events: AgentEvent[];
  selectedAgent: string;
  onSelectAgent: (agent: string) => void;
}) {
  return (
    <section className="panel timeline-panel" aria-label="智能体执行流程">
      <div className="panel-heading">
        <h2>智能体流程</h2>
        <span>{events.length} 条事件</span>
      </div>
      <ol className="agent-list">
        {latestByAgent(events).map(({ agent, event }) => {
          const status = event?.status ?? "queued";
          const Icon =
            status === "completed" ? CheckCircle2 : status === "failed" ? XCircle : status === "running" ? Loader2 : CircleDot;
          return (
            <li className={`agent-step ${status} ${selectedAgent === agent ? "selected" : ""}`} key={agent}>
              <button type="button" onClick={() => onSelectAgent(agent)}>
                <Icon className={status === "running" ? "spin" : ""} size={18} aria-hidden="true" />
                <div>
                  <strong>{AGENT_LABELS[agent] ?? agent}</strong>
                  <p>{event?.message ?? "等待上游智能体输出。"}</p>
                </div>
              </button>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
