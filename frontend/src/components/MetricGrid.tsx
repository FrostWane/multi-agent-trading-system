import { Activity, BarChart3, ShieldAlert, TrendingUp } from "lucide-react";
import type { AnalysisResult } from "../types/analysis";

function percent(value: unknown) {
  return typeof value === "number" ? `${(value * 100).toFixed(2)}%` : "-";
}

const TREND_LABELS: Record<string, string> = {
  bullish: "偏多",
  bearish: "偏空",
  neutral: "震荡",
  insufficient_data: "数据不足",
  unknown: "未知"
};

const RISK_LABELS: Record<string, string> = {
  low: "低",
  medium: "中",
  high: "高"
};

export function MetricGrid({ result }: { result: AnalysisResult | null }) {
  const indicators = result?.indicators ?? {};
  const backtest = result?.backtest ?? {};
  const risk = result?.risk ?? {};

  const metrics = [
    { label: "趋势", value: TREND_LABELS[String(indicators.trend ?? "unknown")] ?? "-", icon: TrendingUp },
    { label: "年化波动率", value: percent(indicators.annualized_volatility), icon: Activity },
    { label: "风险等级", value: risk.level ? `${RISK_LABELS[risk.level] ?? risk.level} / ${risk.score}` : "-", icon: ShieldAlert },
    { label: "回测收益", value: percent(backtest.total_return), icon: BarChart3 }
  ];

  return (
    <section className="metric-grid" aria-label="分析指标">
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
