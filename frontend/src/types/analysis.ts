export type AgentStatus = "queued" | "running" | "completed" | "failed";

export interface AgentEvent {
  run_id: string;
  agent: string;
  status: AgentStatus;
  message: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface AnalyzeRequest {
  symbol: string;
  start_date: string;
  end_date: string;
  horizon: string;
  risk_preference: "conservative" | "balanced" | "aggressive";
}

export interface AnalysisSnapshot {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  request: AnalyzeRequest;
  events: AgentEvent[];
  result: AnalysisResult | null;
  error?: string | null;
}

export interface AnalysisResult {
  engine: string;
  agents: string[];
  market_data_preview: PricePoint[];
  indicators: Record<string, unknown>;
  research: ResearchItem[];
  risk: {
    score?: number;
    level?: string;
    reasons?: string[];
  };
  backtest: {
    total_return?: number;
    benchmark_return?: number;
    max_drawdown?: number;
    win_rate?: number;
    trades?: number;
  };
  report: {
    summary?: string;
    recommendation?: string;
    citations?: Citation[];
    disclaimer?: string;
  };
  critic: {
    passed?: boolean;
    confidence?: string;
    issues?: string[];
  };
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ResearchItem {
  symbol: string;
  title: string;
  source: string;
  published_at: string;
  doc_type: string;
  content: string;
  sentiment: string;
  score: number;
}

export interface Citation {
  title: string;
  source: string;
  published_at: string;
  doc_type: string;
  score: number;
}
