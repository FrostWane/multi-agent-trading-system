import { BadgeCheck, AlertTriangle } from "lucide-react";
import type { AnalysisResult } from "../types/analysis";

const RECOMMENDATION_LABELS: Record<string, string> = {
  watchlist_positive: "积极关注",
  cautious: "谨慎观察",
  neutral: "中性"
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "高",
  medium: "中",
  low: "低"
};

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

function toTextList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) => toDisplayText(item)).filter(Boolean);
  }
  if (typeof value === "string") {
    return value
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean);
  }
  if (value && typeof value === "object") {
    return Object.entries(value).map(([key, item]) => `${key}：${toDisplayText(item)}`);
  }
  return [];
}

export function ReportPanel({ result }: { result: AnalysisResult | null }) {
  const report = result?.report;
  const critic = result?.critic;
  const summary = toDisplayText(report?.summary);
  const recommendation = toDisplayText(report?.recommendation);
  const llmCommentary = toDisplayText(report?.llm_commentary);
  const keyPoints = toTextList(report?.key_points);
  const riskNotes = toTextList(report?.risk_notes);
  const criticIssues = toTextList(critic?.issues);
  const criticSuggestions = toTextList(critic?.suggestions);
  const disclaimer = toDisplayText(report?.disclaimer, "本报告仅用于研究和学习，不构成任何投资建议。");
  const llmError = toDisplayText(report?.llm_error);
  const criticLlmError = toDisplayText(critic?.llm_error);

  return (
    <section className="panel report-panel" aria-label="最终报告">
      <div className="panel-heading">
        <h2>最终报告</h2>
        <span>{result?.engine ?? "待机"}</span>
      </div>
      {summary ? (
        <div className="report-body">
          <p>{summary}</p>
          <div className="report-tags">
            <span>{RECOMMENDATION_LABELS[recommendation] ?? recommendation}</span>
            <span>置信度 {CONFIDENCE_LABELS[critic?.confidence ?? ""] ?? "待定"}</span>
            <span>{critic?.passed ? "校验通过" : "等待校验"}</span>
            <span>{report?.llm_enabled ? "大模型增强" : "规则模式"}</span>
          </div>
          {llmCommentary ? <p className="llm-commentary">{llmCommentary}</p> : null}
          {keyPoints.length > 0 ? (
            <div className="report-list">
              <strong>关键要点</strong>
              <ul>
                {keyPoints.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {riskNotes.length > 0 ? (
            <div className="report-list">
              <strong>风险提示</strong>
              <ul>
                {riskNotes.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {criticIssues.length > 0 ? (
            <div className="critic warning">
              <AlertTriangle size={18} aria-hidden="true" />
              <span>{criticIssues.join(", ")}</span>
            </div>
          ) : (
            <div className="critic">
              <BadgeCheck size={18} aria-hidden="true" />
              <span>结论校验完成</span>
            </div>
          )}
          {criticSuggestions.length > 0 ? (
            <div className="report-list">
              <strong>校验建议</strong>
              <ul>
                {criticSuggestions.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {llmError ? <small>大模型报告兜底原因：{llmError}</small> : null}
          {criticLlmError ? <small>大模型校验兜底原因：{criticLlmError}</small> : null}
          <small>{disclaimer}</small>
        </div>
      ) : (
        <p className="empty">暂无报告。</p>
      )}
    </section>
  );
}
