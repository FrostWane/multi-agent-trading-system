import { FileSearch } from "lucide-react";
import type { ResearchItem } from "../types/analysis";

function toDisplayText(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return fallback;
  }
}

export function EvidencePanel({ research }: { research: ResearchItem[] }) {
  return (
    <section className="panel evidence-panel" aria-label="RAG 证据">
      <div className="panel-heading">
        <h2>RAG 证据</h2>
        <span>{research.length} 篇文档</span>
      </div>
      <div className="evidence-list">
        {research.length === 0 ? (
          <p className="empty">暂无引用证据。</p>
        ) : (
          research.map((item, index) => (
            <article className="evidence-item" key={`${toDisplayText(item.source)}-${toDisplayText(item.title)}-${index}`}>
              <FileSearch size={18} aria-hidden="true" />
              <div>
                <strong>{toDisplayText(item.title, "未命名文档")}</strong>
                <p>{toDisplayText(item.content)}</p>
                <span>
                  {toDisplayText(item.source, "unknown")} · {toDisplayText(item.published_at, "未知日期")} · 相关度{" "}
                  {toDisplayText(item.score, "-")}
                </span>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
