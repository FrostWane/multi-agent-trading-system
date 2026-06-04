from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RiskPreference = Literal["conservative", "balanced", "aggressive"]
StrategySet = Literal["compare_all", "ma_cross", "momentum", "rsi_reversal"]


class BacktestConfig(BaseModel):
    strategy_set: StrategySet = "compare_all"
    short_window: int = Field(default=5, ge=2, le=120)
    long_window: int = Field(default=20, ge=3, le=250)
    momentum_window: int = Field(default=20, ge=2, le=250)
    rsi_window: int = Field(default=14, ge=2, le=120)
    rsi_buy_threshold: float = Field(default=30, ge=1, le=50)
    rsi_sell_threshold: float = Field(default=70, ge=50, le=99)
    initial_cash: float = Field(default=100000, ge=1000)
    fee_rate: float = Field(default=0.0003, ge=0, le=0.02)


class AnalyzeRequest(BaseModel):
    symbol: str = Field(default="000001", min_length=6, max_length=9)
    start_date: date = Field(default=date(2026, 1, 1))
    end_date: date = Field(default_factory=date.today)
    horizon: str = Field(default="1m", description="Analysis horizon, for example 1w, 1m, 3m")
    risk_preference: RiskPreference = "balanced"
    backtest_config: BacktestConfig = Field(default_factory=BacktestConfig)


class AnalyzeResponse(BaseModel):
    run_id: str
    status: str


class RagIngestRequest(BaseModel):
    symbol: str = "000001"
    title: str
    source: str = "manual"
    doc_type: str = "note"
    content: str


class AgentEvent(BaseModel):
    run_id: str
    agent: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class AnalysisSnapshot(BaseModel):
    run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    request: dict[str, Any]
    events: list[AgentEvent]
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
