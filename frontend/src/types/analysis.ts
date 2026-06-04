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
  backtest_config: BacktestConfig;
}

export interface BacktestConfig {
  strategy_set: "compare_all" | "ma_cross" | "momentum" | "rsi_reversal";
  short_window: number;
  long_window: number;
  momentum_window: number;
  rsi_window: number;
  rsi_buy_threshold: number;
  rsi_sell_threshold: number;
  initial_cash: number;
  fee_rate: number;
}

export interface StockOption {
  symbol: string;
  name: string;
  market: string;
}

export interface RagIngestPayload {
  symbol: string;
  title: string;
  source: string;
  doc_type: string;
  content: string;
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
    strategy?: string;
    strategy_label?: string;
    best_strategy?: string;
    best_strategy_label?: string;
    selected_strategy?: string;
    parameters?: BacktestConfig;
    total_return?: number;
    annualized_return?: number;
    benchmark_return?: number;
    max_drawdown?: number;
    sharpe?: number;
    win_rate?: number;
    trades?: number;
    final_equity?: number;
    equity_curve?: EquityPoint[];
    strategies?: BacktestStrategy[];
  };
  report: {
    summary?: string;
    recommendation?: string;
    citations?: Citation[];
    disclaimer?: string;
    llm_enabled?: boolean;
    llm_commentary?: string;
    key_points?: string[];
    risk_notes?: string[];
    llm_error?: string;
  };
  critic: {
    passed?: boolean;
    confidence?: string;
    issues?: string[];
    suggestions?: string[];
    llm_enabled?: boolean;
    llm_error?: string;
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

export interface EquityPoint {
  date: string;
  equity: number;
  benchmark: number;
}

export interface BacktestStrategy {
  strategy: string;
  label: string;
  parameters: Record<string, unknown>;
  total_return: number;
  annualized_return: number;
  benchmark_return: number;
  max_drawdown: number;
  sharpe: number;
  win_rate: number;
  trades: number;
  final_equity: number;
  equity_curve: EquityPoint[];
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
