import { FileSearch } from "lucide-react";
import type { ResearchItem } from "../types/analysis";

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
          research.map((item) => (
            <article className="evidence-item" key={`${item.source}-${item.title}`}>
              <FileSearch size={18} aria-hidden="true" />
              <div>
                <strong>{item.title}</strong>
                <p>{item.content}</p>
                <span>
                  {item.source} · {item.published_at} · 相关度 {item.score}
                </span>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
