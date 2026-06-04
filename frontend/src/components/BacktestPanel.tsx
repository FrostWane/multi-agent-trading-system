import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { AnalysisResult, BacktestStrategy } from "../types/analysis";

function percent(value: number | undefined) {
  return typeof value === "number" ? `${(value * 100).toFixed(2)}%` : "-";
}

function money(value: number | undefined) {
  return typeof value === "number" ? value.toLocaleString("zh-CN", { maximumFractionDigits: 0 }) : "-";
}

function strategyRows(strategies: BacktestStrategy[] | undefined) {
  return [...(strategies ?? [])].sort((left, right) => right.total_return - left.total_return);
}

export function BacktestPanel({ result }: { result: AnalysisResult | null }) {
  const backtest = result?.backtest;
  const rows = strategyRows(backtest?.strategies);
  const curve = backtest?.equity_curve ?? [];

  return (
    <section className="panel backtest-panel" aria-label="策略回测对比">
      <div className="panel-heading">
        <div>
          <h2>策略回测对比</h2>
          <p>{backtest?.best_strategy_label ? `最佳策略：${backtest.best_strategy_label}` : "等待分析结果"}</p>
        </div>
        <span>{rows.length} 个策略</span>
      </div>
      {backtest ? (
        <>
          <div className="backtest-summary">
            <div>
              <span>策略收益</span>
              <strong>{percent(backtest.total_return)}</strong>
            </div>
            <div>
              <span>基准收益</span>
              <strong>{percent(backtest.benchmark_return)}</strong>
            </div>
            <div>
              <span>最大回撤</span>
              <strong>{percent(backtest.max_drawdown)}</strong>
            </div>
            <div>
              <span>夏普比率</span>
              <strong>{backtest.sharpe?.toFixed(2) ?? "-"}</strong>
            </div>
          </div>
          <div className="backtest-chart">
            {curve.length === 0 ? (
              <p className="empty">暂无权益曲线。</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={curve}>
                  <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
                  <YAxis tick={{ fontSize: 11 }} width={64} tickFormatter={(value) => money(Number(value))} />
                  <Tooltip formatter={(value) => money(Number(value))} />
                  <Line type="monotone" dataKey="equity" name="策略权益" stroke="#2563eb" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="benchmark" name="买入持有" stroke="#64748b" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="strategy-table-wrap">
            <table className="strategy-table">
              <thead>
                <tr>
                  <th>策略</th>
                  <th>收益</th>
                  <th>年化</th>
                  <th>回撤</th>
                  <th>夏普</th>
                  <th>胜率</th>
                  <th>交易</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((item) => (
                  <tr key={item.strategy} className={item.strategy === backtest.best_strategy ? "best" : ""}>
                    <td>{item.label}</td>
                    <td>{percent(item.total_return)}</td>
                    <td>{percent(item.annualized_return)}</td>
                    <td>{percent(item.max_drawdown)}</td>
                    <td>{item.sharpe.toFixed(2)}</td>
                    <td>{percent(item.win_rate)}</td>
                    <td>{item.trades}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <p className="empty">暂无回测结果。</p>
      )}
    </section>
  );
}
