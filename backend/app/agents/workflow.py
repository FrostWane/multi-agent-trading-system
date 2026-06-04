from __future__ import annotations

from typing import Any

from app.agents.state import AnalysisState, EmitEvent
from app.services.backtest import run_moving_average_backtest
from app.services.data_provider import MarketDataProvider
from app.services.indicators import summarize_indicators
from app.services.rag import search_market_docs
from app.services.report import build_report
from app.services.risk import assess_risk


AGENT_SEQUENCE = [
    "Supervisor Agent",
    "Market Data Agent",
    "Quant Analyst Agent",
    "RAG Research Agent",
    "Risk Agent",
    "Backtest Agent",
    "Report Agent",
    "Critic Agent",
]


def _emit(
    emit: EmitEvent | None,
    agent: str,
    status: str,
    message: str,
    payload: dict[str, Any] | None = None,
) -> None:
    if emit:
        emit(agent, status, message, payload)


def _supervisor_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Supervisor Agent", "running", "Decomposing the analysis request.")
    state["plan"] = AGENT_SEQUENCE[1:]
    _emit(
        emit,
        "Supervisor Agent",
        "completed",
        "Created a specialist-agent execution plan.",
        {"plan": state["plan"]},
    )
    return state


def _market_data_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    request = state["request"]
    _emit(emit, "Market Data Agent", "running", "Fetching A-share market history.")
    provider = MarketDataProvider()
    state["market_data"] = provider.get_stock_history(
        symbol=request["symbol"],
        start_date=request["start_date"],
        end_date=request["end_date"],
    )
    _emit(
        emit,
        "Market Data Agent",
        "completed",
        f"Loaded {len(state['market_data'])} OHLCV rows.",
        {"rows": len(state["market_data"])},
    )
    return state


def _quant_analyst_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Quant Analyst Agent", "running", "Calculating trend and momentum factors.")
    state["indicators"] = summarize_indicators(state.get("market_data", []))
    _emit(
        emit,
        "Quant Analyst Agent",
        "completed",
        "Generated MA, RSI, MACD, volatility, and drawdown features.",
        state["indicators"],
    )
    return state


def _rag_research_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    request = state["request"]
    _emit(emit, "RAG Research Agent", "running", "Retrieving market evidence from RAG store.")
    query = (
        f"{request['symbol']} {state.get('indicators', {}).get('trend', '')} "
        f"risk earnings industry news research"
    )
    state["research"] = search_market_docs(request["symbol"], query=query, limit=5)
    _emit(
        emit,
        "RAG Research Agent",
        "completed",
        f"Retrieved {len(state['research'])} evidence documents.",
        {"citations": [item["title"] for item in state["research"]]},
    )
    return state


def _risk_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Risk Agent", "running", "Scoring volatility, drawdown, and evidence risk.")
    state["risk"] = assess_risk(
        state.get("indicators", {}),
        state.get("research", []),
        state["request"].get("risk_preference", "balanced"),
    )
    _emit(emit, "Risk Agent", "completed", "Produced a risk profile.", state["risk"])
    return state


def _backtest_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Backtest Agent", "running", "Running MA crossover strategy backtest.")
    state["backtest"] = run_moving_average_backtest(state.get("market_data", []))
    _emit(
        emit,
        "Backtest Agent",
        "completed",
        "Backtest metrics are ready.",
        state["backtest"],
    )
    return state


def _report_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Report Agent", "running", "Synthesizing specialist findings.")
    state["report"] = build_report(state)
    _emit(
        emit,
        "Report Agent",
        "completed",
        "Generated the structured research report.",
        {"recommendation": state["report"]["recommendation"]},
    )
    return state


def _critic_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Critic Agent", "running", "Validating report confidence and citations.")
    report = state.get("report", {})
    issues: list[str] = []
    if not state.get("market_data"):
        issues.append("market data is missing")
    if not report.get("citations"):
        issues.append("RAG citations are missing")
    if state.get("risk", {}).get("level") == "high" and report.get("recommendation") != "cautious":
        issues.append("high risk should produce a cautious recommendation")

    state["critic"] = {
        "passed": not issues,
        "issues": issues,
        "confidence": "medium" if issues else "high",
    }
    _emit(
        emit,
        "Critic Agent",
        "completed",
        "Review completed." if not issues else "Review found issues.",
        state["critic"],
    )
    return state


def _run_sequential(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    for node in [
        _supervisor_agent,
        _market_data_agent,
        _quant_analyst_agent,
        _rag_research_agent,
        _risk_agent,
        _backtest_agent,
        _report_agent,
        _critic_agent,
    ]:
        state = node(state, emit)
    state["engine"] = "sequential-fallback"
    return state


def _run_langgraph(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception:
        return _run_sequential(state, emit)

    graph = StateGraph(AnalysisState)
    graph.add_node("supervisor", lambda graph_state: _supervisor_agent(graph_state, emit))
    graph.add_node("market_data", lambda graph_state: _market_data_agent(graph_state, emit))
    graph.add_node("quant", lambda graph_state: _quant_analyst_agent(graph_state, emit))
    graph.add_node("rag", lambda graph_state: _rag_research_agent(graph_state, emit))
    graph.add_node("risk", lambda graph_state: _risk_agent(graph_state, emit))
    graph.add_node("backtest", lambda graph_state: _backtest_agent(graph_state, emit))
    graph.add_node("report", lambda graph_state: _report_agent(graph_state, emit))
    graph.add_node("critic", lambda graph_state: _critic_agent(graph_state, emit))

    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "market_data")
    graph.add_edge("market_data", "quant")
    graph.add_edge("quant", "rag")
    graph.add_edge("rag", "risk")
    graph.add_edge("risk", "backtest")
    graph.add_edge("backtest", "report")
    graph.add_edge("report", "critic")
    graph.add_edge("critic", END)

    compiled = graph.compile()
    result = compiled.invoke(state)
    result["engine"] = "langgraph"
    return result


def run_analysis_workflow(request: dict[str, Any], emit: EmitEvent | None = None) -> dict[str, Any]:
    state: AnalysisState = {"request": request}
    result = _run_langgraph(state, emit)
    return {
        "request": result["request"],
        "engine": result.get("engine", "unknown"),
        "agents": AGENT_SEQUENCE,
        "plan": result.get("plan", []),
        "market_data_preview": result.get("market_data", [])[-30:],
        "indicators": result.get("indicators", {}),
        "research": result.get("research", []),
        "risk": result.get("risk", {}),
        "backtest": result.get("backtest", {}),
        "report": result.get("report", {}),
        "critic": result.get("critic", {}),
    }
