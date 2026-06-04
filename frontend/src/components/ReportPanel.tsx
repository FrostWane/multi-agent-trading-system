import { BadgeCheck, AlertTriangle } from "lucide-react";
import type { AnalysisResult } from "../types/analysis";

export function ReportPanel({ result }: { result: AnalysisResult | null }) {
  const report = result?.report;
  const critic = result?.critic;

  return (
    <section className="panel report-panel" aria-label="Final report">
      <div className="panel-heading">
        <h2>Report</h2>
        <span>{result?.engine ?? "idle"}</span>
      </div>
      {report?.summary ? (
        <div className="report-body">
          <p>{report.summary}</p>
          <div className="report-tags">
            <span>{report.recommendation}</span>
            <span>{critic?.confidence ?? "pending"} confidence</span>
            <span>{critic?.passed ? "critic passed" : "critic pending"}</span>
          </div>
          {critic?.issues && critic.issues.length > 0 ? (
            <div className="critic warning">
              <AlertTriangle size={18} aria-hidden="true" />
              <span>{critic.issues.join(", ")}</span>
            </div>
          ) : (
            <div className="critic">
              <BadgeCheck size={18} aria-hidden="true" />
              <span>Validation complete</span>
            </div>
          )}
          <small>{report.disclaimer}</small>
        </div>
      ) : (
        <p className="empty">No report yet.</p>
      )}
    </section>
  );
}
