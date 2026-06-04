import { DatabaseZap, Send } from "lucide-react";
import { useState } from "react";
import { ingestRagDocument } from "../lib/api";
import type { RagIngestPayload } from "../types/analysis";

interface RagIngestPanelProps {
  symbol: string;
}

export function RagIngestPanel({ symbol }: RagIngestPanelProps) {
  const [form, setForm] = useState<RagIngestPayload>({
    symbol,
    title: "",
    source: "manual",
    doc_type: "note",
    content: ""
  });
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setStatus("");
    setError("");
    try {
      const payload = { ...form, symbol };
      const result = await ingestRagDocument(payload);
      setStatus(`已导入，当前文档数 ${result.count}`);
      setForm({ ...payload, title: "", content: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "文档导入失败");
    }
  }

  return (
    <section className="panel rag-ingest-panel" aria-label="RAG 文档导入">
      <div className="panel-heading">
        <h2>RAG 导入</h2>
        <DatabaseZap size={18} aria-hidden="true" />
      </div>
      <form className="rag-form" onSubmit={handleSubmit}>
        <label>
          标题
          <input
            required
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
          />
        </label>
        <div className="two-col">
          <label>
            来源
            <input value={form.source} onChange={(event) => setForm({ ...form, source: event.target.value })} />
          </label>
          <label>
            类型
            <select value={form.doc_type} onChange={(event) => setForm({ ...form, doc_type: event.target.value })}>
              <option value="note">笔记</option>
              <option value="news">新闻</option>
              <option value="announcement">公告</option>
              <option value="research_note">研报</option>
            </select>
          </label>
        </div>
        <label>
          内容
          <textarea
            required
            rows={6}
            value={form.content}
            onChange={(event) => setForm({ ...form, content: event.target.value })}
          />
        </label>
        <button type="submit" title="导入 RAG 文档">
          <Send size={16} aria-hidden="true" />
          导入
        </button>
        {status ? <p className="success">{status}</p> : null}
        {error ? <p className="error">{error}</p> : null}
      </form>
    </section>
  );
}
