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

export function ReportPanel({ result }: { result: AnalysisResult | null }) {
  const report = result?.report;
  const critic = result?.critic;

  return (
    <section className="panel report-panel" aria-label="最终报告">
      <div className="panel-heading">
        <h2>最终报告</h2>
        <span>{result?.engine ?? "待机"}</span>
      </div>
      {report?.summary ? (
        <div className="report-body">
          <p>{report.summary}</p>
          <div className="report-tags">
            <span>{RECOMMENDATION_LABELS[report.recommendation ?? ""] ?? report.recommendation}</span>
            <span>置信度 {CONFIDENCE_LABELS[critic?.confidence ?? ""] ?? "待定"}</span>
            <span>{critic?.passed ? "校验通过" : "等待校验"}</span>
            <span>{report.llm_enabled ? "大模型增强" : "规则模式"}</span>
          </div>
          {report.llm_commentary ? <p className="llm-commentary">{report.llm_commentary}</p> : null}
          {report.key_points && report.key_points.length > 0 ? (
            <div className="report-list">
              <strong>关键要点</strong>
              <ul>
                {report.key_points.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {report.risk_notes && report.risk_notes.length > 0 ? (
            <div className="report-list">
              <strong>风险提示</strong>
              <ul>
                {report.risk_notes.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {critic?.issues && critic.issues.length > 0 ? (
            <div className="critic warning">
              <AlertTriangle size={18} aria-hidden="true" />
              <span>{critic.issues.join(", ")}</span>
            </div>
          ) : (
            <div className="critic">
              <BadgeCheck size={18} aria-hidden="true" />
              <span>结论校验完成</span>
            </div>
          )}
          {critic?.suggestions && critic.suggestions.length > 0 ? (
            <div className="report-list">
              <strong>校验建议</strong>
              <ul>
                {critic.suggestions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {report.llm_error ? <small>大模型报告兜底原因：{report.llm_error}</small> : null}
          {critic?.llm_error ? <small>大模型校验兜底原因：{critic.llm_error}</small> : null}
          <small>{report.disclaimer}</small>
        </div>
      ) : (
        <p className="empty">暂无报告。</p>
      )}
    </section>
  );
}
