from __future__ import annotations

from typing import Any, Callable, Optional, TypedDict


EmitEvent = Callable[[str, str, str, Optional[dict[str, Any]]], None]


class AnalysisState(TypedDict, total=False):
    request: dict[str, Any]
    plan: list[str]
    market_data: list[dict[str, Any]]
    indicators: dict[str, Any]
    research: list[dict[str, Any]]
    risk: dict[str, Any]
    backtest: dict[str, Any]
    report: dict[str, Any]
    critic: dict[str, Any]
    engine: str
