import { Activity, BarChart3, ShieldAlert, TrendingUp } from "lucide-react";
import type { AnalysisResult } from "../types/analysis";

function percent(value: unknown) {
  return typeof value === "number" ? `${(value * 100).toFixed(2)}%` : "-";
}

export function MetricGrid({ result }: { result: AnalysisResult | null }) {
  const indicators = result?.indicators ?? {};
  const backtest = result?.backtest ?? {};
  const risk = result?.risk ?? {};

  const metrics = [
    { label: "Trend", value: String(indicators.trend ?? "-"), icon: TrendingUp },
    { label: "Volatility", value: percent(indicators.annualized_volatility), icon: Activity },
    { label: "Risk", value: risk.level ? `${risk.level} / ${risk.score}` : "-", icon: ShieldAlert },
    { label: "Backtest", value: percent(backtest.total_return), icon: BarChart3 }
  ];

  return (
    <section className="metric-grid" aria-label="Analysis metrics">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div className="metric" key={metric.label}>
            <Icon size={18} aria-hidden="true" />
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        );
      })}
    </section>
  );
}
