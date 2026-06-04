import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { PricePoint } from "../types/analysis";

export function PriceChart({ data }: { data: PricePoint[] }) {
  return (
    <section className="panel chart-panel" aria-label="价格走势">
      <div className="panel-heading">
        <h2>价格走势</h2>
        <span>{data.length} 个点位</span>
      </div>
      <div className="chart-frame">
        {data.length === 0 ? (
          <p className="empty chart-empty">暂无价格数据。</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="closeFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
              <YAxis domain={["dataMin - 1", "dataMax + 1"]} tick={{ fontSize: 11 }} width={48} />
              <Tooltip />
              <Area type="monotone" dataKey="close" stroke="#2563eb" fill="url(#closeFill)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
