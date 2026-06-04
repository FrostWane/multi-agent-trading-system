from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RiskPreference = Literal["conservative", "balanced", "aggressive"]


class AnalyzeRequest(BaseModel):
    symbol: str = Field(default="000001", min_length=6, max_length=9)
    start_date: date = Field(default=date(2024, 1, 1))
    end_date: date = Field(default=date(2024, 12, 31))
    horizon: str = Field(default="1m", description="Analysis horizon, for example 1w, 1m, 3m")
    risk_preference: RiskPreference = "balanced"


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
