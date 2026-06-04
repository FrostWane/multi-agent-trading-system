import { FileSearch } from "lucide-react";
import type { ResearchItem } from "../types/analysis";

export function EvidencePanel({ research }: { research: ResearchItem[] }) {
  return (
    <section className="panel evidence-panel" aria-label="RAG evidence">
      <div className="panel-heading">
        <h2>Evidence</h2>
        <span>{research.length} docs</span>
      </div>
      <div className="evidence-list">
        {research.length === 0 ? (
          <p className="empty">No citations yet.</p>
        ) : (
          research.map((item) => (
            <article className="evidence-item" key={`${item.source}-${item.title}`}>
              <FileSearch size={18} aria-hidden="true" />
              <div>
                <strong>{item.title}</strong>
                <p>{item.content}</p>
                <span>
                  {item.source} · {item.published_at} · score {item.score}
                </span>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
