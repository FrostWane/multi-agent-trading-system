from __future__ import annotations

from typing import Any

from app.agents.state import AnalysisState, EmitEvent
from app.services.backtest import run_strategy_comparison
from app.services.data_provider import MarketDataProvider
from app.services.indicators import summarize_indicators
from app.services.rag import search_market_docs
from app.services.llm import llm_available
from app.services.report import build_llm_report, review_report_with_llm
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
    _emit(emit, "Supervisor Agent", "running", "正在拆解分析请求。")
    state["plan"] = AGENT_SEQUENCE[1:]
    _emit(
        emit,
        "Supervisor Agent",
        "completed",
        "已生成专业智能体执行计划。",
        {"plan": state["plan"]},
    )
    return state


def _market_data_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    request = state["request"]
    _emit(emit, "Market Data Agent", "running", "正在获取 A 股历史行情。")
    provider = MarketDataProvider()
    market_payload = provider.get_stock_history_with_meta(
        symbol=request["symbol"],
        start_date=request["start_date"],
        end_date=request["end_date"],
    )
    state["market_data"] = market_payload["rows"]
    state["market_data_metadata"] = market_payload["metadata"]
    source_label = state["market_data_metadata"].get("provider_label", "未知数据源")
    adjust_label = state["market_data_metadata"].get("adjust_label", "未知复权")
    _emit(
        emit,
        "Market Data Agent",
        "completed",
        f"已从 {source_label}（{adjust_label}）加载 {len(state['market_data'])} 条 OHLCV 行情数据。",
        {"rows": len(state["market_data"]), "market_data_meta": state["market_data_metadata"]},
    )
    return state


def _quant_analyst_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Quant Analyst Agent", "running", "正在计算趋势和动量因子。")
    state["indicators"] = summarize_indicators(state.get("market_data", []))
    _emit(
        emit,
        "Quant Analyst Agent",
        "completed",
        "已生成均线、RSI、MACD、波动率和回撤指标。",
        state["indicators"],
    )
    return state


def _rag_research_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    request = state["request"]
    _emit(emit, "RAG Research Agent", "running", "正在从 RAG 知识库检索市场证据。")
    query = (
        f"{request['symbol']} {state.get('indicators', {}).get('trend', '')} "
        f"risk earnings industry news research"
    )
    state["research"] = search_market_docs(request["symbol"], query=query, limit=5)
    _emit(
        emit,
        "RAG Research Agent",
        "completed",
        f"已检索到 {len(state['research'])} 篇证据文档。",
        {"citations": [item["title"] for item in state["research"]]},
    )
    return state


def _risk_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Risk Agent", "running", "正在评估波动率、回撤和证据风险。")
    state["risk"] = assess_risk(
        state.get("indicators", {}),
        state.get("research", []),
        state["request"].get("risk_preference", "balanced"),
    )
    _emit(emit, "Risk Agent", "completed", "已生成风险画像。", state["risk"])
    return state


def _backtest_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Backtest Agent", "running", "正在执行多策略回测对比。")
    state["backtest"] = run_strategy_comparison(
        state.get("market_data", []),
        state["request"].get("backtest_config", {}),
    )
    _emit(
        emit,
        "Backtest Agent",
        "completed",
        "多策略回测指标已生成。",
        {
            "best_strategy": state["backtest"].get("best_strategy_label"),
            "total_return": state["backtest"].get("total_return"),
            "strategy_count": len(state["backtest"].get("strategies", [])),
        },
    )
    return state


def _report_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    message = "正在调用大模型生成中文研究报告。" if llm_available() else "正在综合各智能体结论。"
    _emit(emit, "Report Agent", "running", message)
    state["report"] = build_llm_report(state)
    _emit(
        emit,
        "Report Agent",
        "completed",
        "已生成大模型增强研究报告。" if state["report"].get("llm_enabled") else "已生成结构化研究报告。",
        {
            "recommendation": state["report"]["recommendation"],
            "llm_enabled": state["report"].get("llm_enabled", False),
        },
    )
    return state


def _critic_agent(state: AnalysisState, emit: EmitEvent | None) -> AnalysisState:
    _emit(emit, "Critic Agent", "running", "正在校验报告置信度和引用完整性。")
    report = state.get("report", {})
    issues: list[str] = []
    if not state.get("market_data"):
        issues.append("缺少行情数据")
    if not report.get("citations"):
        issues.append("缺少 RAG 引用证据")
    if state.get("risk", {}).get("level") == "high" and report.get("recommendation") != "cautious":
        issues.append("高风险场景应给出谨慎建议")

    rule_review = {
        "passed": not issues,
        "issues": issues,
        "confidence": "medium" if issues else "high",
        "llm_enabled": False,
    }
    state["critic"] = review_report_with_llm(state, rule_review)
    _emit(
        emit,
        "Critic Agent",
        "completed",
        "校验完成。" if not issues else "校验发现问题。",
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
        "market_data_meta": result.get("market_data_metadata", {}),
        "market_data_preview": result.get("market_data", [])[-30:],
        "indicators": result.get("indicators", {}),
        "research": result.get("research", []),
        "risk": result.get("risk", {}),
        "backtest": result.get("backtest", {}),
        "report": result.get("report", {}),
        "critic": result.get("critic", {}),
    }
