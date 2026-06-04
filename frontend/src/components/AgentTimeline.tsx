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

function latestByAgent(events: AgentEvent[]) {
  return AGENTS.map((agent) => {
    const latest = [...events].reverse().find((event) => event.agent === agent);
    return { agent, event: latest };
  });
}

export function AgentTimeline({ events }: { events: AgentEvent[] }) {
  return (
    <section className="panel timeline-panel" aria-label="Agent execution timeline">
      <div className="panel-heading">
        <h2>Agent Flow</h2>
        <span>{events.length} events</span>
      </div>
      <ol className="agent-list">
        {latestByAgent(events).map(({ agent, event }) => {
          const status = event?.status ?? "queued";
          const Icon =
            status === "completed" ? CheckCircle2 : status === "failed" ? XCircle : status === "running" ? Loader2 : CircleDot;
          return (
            <li className={`agent-step ${status}`} key={agent}>
              <Icon className={status === "running" ? "spin" : ""} size={18} aria-hidden="true" />
              <div>
                <strong>{agent}</strong>
                <p>{event?.message ?? "Waiting for upstream signal."}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
