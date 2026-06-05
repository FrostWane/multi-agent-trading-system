import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { MarketDataMeta, PricePoint } from "../types/analysis";

interface CandlePoint extends PricePoint {
  ma5: number | null;
  ma20: number | null;
  changePct: number;
  color: string;
}

interface CandleShapeProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  payload?: CandlePoint;
  yAxis?: {
    scale: (value: number) => number;
  };
}

const PROVIDER_LABELS: Record<string, string> = {
  akshare: "AkShare",
  eastmoney: "东方财富",
  tencent: "腾讯证券",
  sample: "Sample 模拟数据"
};

const ADJUST_LABELS: Record<string, string> = {
  qfq: "前复权",
  hfq: "后复权",
  none: "未复权"
};

function movingAverage(data: PricePoint[], window: number, index: number) {
  if (index + 1 < window) return null;
  const slice = data.slice(index + 1 - window, index + 1);
  return Number((slice.reduce((sum, item) => sum + item.close, 0) / window).toFixed(2));
}

function enrich(data: PricePoint[]): CandlePoint[] {
  return data.map((item, index) => {
    const previous = data[index - 1]?.close ?? item.open;
    const changePct = previous ? (item.close / previous - 1) * 100 : 0;
    return {
      ...item,
      ma5: movingAverage(data, 5, index),
      ma20: movingAverage(data, 20, index),
      changePct,
      color: item.close >= item.open ? "#dc2626" : "#16a34a"
    };
  });
}

function CandleShape(props: CandleShapeProps) {
  const { x = 0, width = 0, payload, yAxis } = props;
  if (!payload || !yAxis) return null;

  const center = x + width / 2;
  const candleWidth = Math.max(4, Math.min(14, width * 0.58));
  const openY = yAxis.scale(payload.open);
  const closeY = yAxis.scale(payload.close);
  const highY = yAxis.scale(payload.high);
  const lowY = yAxis.scale(payload.low);
  const bodyY = Math.min(openY, closeY);
  const bodyHeight = Math.max(2, Math.abs(closeY - openY));
  const color = payload.color;

  return (
    <g>
      <line x1={center} x2={center} y1={highY} y2={lowY} stroke={color} strokeWidth={1.2} />
      <rect
        x={center - candleWidth / 2}
        y={bodyY}
        width={candleWidth}
        height={bodyHeight}
        fill={color}
        rx={1}
      />
    </g>
  );
}

function formatVolume(value: number) {
  if (value >= 100000000) return `${(value / 100000000).toFixed(2)}亿`;
  if (value >= 10000) return `${(value / 10000).toFixed(0)}万`;
  return String(Math.round(value));
}

function tooltipContent({ active, payload }: { active?: boolean; payload?: Array<{ payload?: CandlePoint }> }) {
  const item = payload?.[0]?.payload;
  if (!active || !item) return null;
  return (
    <div className="kline-tooltip">
      <strong>{item.date}</strong>
      <span>开盘：{item.open.toFixed(2)}</span>
      <span>最高：{item.high.toFixed(2)}</span>
      <span>最低：{item.low.toFixed(2)}</span>
      <span>收盘：{item.close.toFixed(2)}</span>
      <span className={item.changePct >= 0 ? "rise" : "fall"}>涨跌幅：{item.changePct.toFixed(2)}%</span>
      <span>成交量：{formatVolume(item.volume)}</span>
      <span>MA5：{item.ma5?.toFixed(2) ?? "-"}</span>
      <span>MA20：{item.ma20?.toFixed(2) ?? "-"}</span>
    </div>
  );
}

export function PriceChart({ data, meta }: { data: PricePoint[]; meta?: MarketDataMeta }) {
  const chartData = enrich(data);
  const latest = chartData[chartData.length - 1];
  const providerCode = meta?.provider ?? "";
  const adjustCode = meta?.adjust ?? "";
  const sourceLabel = PROVIDER_LABELS[providerCode] ?? meta?.provider_label ?? "待获取数据源";
  const adjustLabel = adjustCode ? ` · ${ADJUST_LABELS[adjustCode] ?? meta?.adjust_label ?? adjustCode}` : "";

  return (
    <section className="panel chart-panel" aria-label="专业 K 线图">
      <div className="panel-heading">
        <div>
          <h2>K 线走势</h2>
          <p>{latest ? `${latest.date} 收盘 ${latest.close.toFixed(2)}` : "暂无行情"}</p>
        </div>
        <div className="chart-meta">
          <span className={meta?.is_sample ? "data-source sample" : "data-source"}>
            {sourceLabel}
            {adjustLabel}
          </span>
          <span>{data.length} 个交易日</span>
        </div>
      </div>
      {meta?.is_sample ? (
        <p className="source-warning">
          当前使用 Sample 模拟行情，价格不会与同花顺一致。真实行情请安装 AkShare 或关闭 sample 兜底。
          {meta.fallback_reason ? ` 兜底原因：${meta.fallback_reason}` : ""}
        </p>
      ) : null}
      <div className="kline-legend">
        <span className="legend-rise">上涨</span>
        <span className="legend-fall">下跌</span>
        <span className="legend-ma5">MA5</span>
        <span className="legend-ma20">MA20</span>
      </div>
      <div className="chart-frame kline-frame">
        {chartData.length === 0 ? (
          <p className="empty chart-empty">暂无价格数据。</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 12, right: 12, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                minTickGap={24}
                xAxisId="price"
                height={24}
              />
              <XAxis dataKey="date" xAxisId="volume" hide />
              <YAxis
                yAxisId="price"
                orientation="right"
                domain={["dataMin - 1", "dataMax + 1"]}
                tick={{ fontSize: 11 }}
                width={52}
              />
              <YAxis yAxisId="volume" hide domain={[0, "dataMax * 3"]} />
              <Tooltip content={tooltipContent} />
              <ReferenceLine
                xAxisId="price"
                yAxisId="price"
                y={latest?.close}
                stroke="#94a3b8"
                strokeDasharray="4 4"
              />
              <Bar
                dataKey="close"
                yAxisId="price"
                xAxisId="price"
                shape={<CandleShape />}
                isAnimationActive={false}
              />
              <Bar
                dataKey="volume"
                yAxisId="volume"
                xAxisId="volume"
                barSize={6}
                fill="#cbd5e1"
                opacity={0.72}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="ma5"
                yAxisId="price"
                xAxisId="price"
                stroke="#f59e0b"
                strokeWidth={1.8}
                dot={false}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="ma20"
                yAxisId="price"
                xAxisId="price"
                stroke="#2563eb"
                strokeWidth={1.8}
                dot={false}
                connectNulls
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
