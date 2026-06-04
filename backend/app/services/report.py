from __future__ import annotations

from typing import Any

from app.services.llm import llm_client, llm_available


def build_report(state: dict) -> dict:
    request = state["request"]
    indicators = state.get("indicators", {})
    risk = state.get("risk", {})
    backtest = state.get("backtest", {})
    research = state.get("research", [])

    trend = indicators.get("trend", "unknown")
    risk_level = risk.get("level", "unknown")
    strategy_return = backtest.get("total_return", 0)
    benchmark_return = backtest.get("benchmark_return", 0)
    strategy_label = backtest.get("best_strategy_label") or backtest.get("strategy_label") or "策略"

    recommendation = "neutral"
    if trend == "bullish" and risk_level != "high" and strategy_return >= benchmark_return:
        recommendation = "watchlist_positive"
    elif risk_level == "high" or trend == "bearish":
        recommendation = "cautious"

    trend_labels = {
        "bullish": "偏多",
        "bearish": "偏空",
        "neutral": "震荡",
        "insufficient_data": "数据不足",
        "unknown": "未知",
    }
    risk_labels = {"low": "低", "medium": "中", "high": "高", "unknown": "未知"}
    summary = (
        f"{request['symbol']} 当前技术面呈现{trend_labels.get(trend, trend)}特征，"
        f"综合风险等级为{risk_labels.get(risk_level, risk_level)}。"
        f"回测中表现较好的{strategy_label}区间收益为 {strategy_return:.2%}，"
        f"同期买入并持有收益为 {benchmark_return:.2%}。"
    )

    citations = [
        {
            "title": item["title"],
            "source": item["source"],
            "published_at": item["published_at"],
            "doc_type": item["doc_type"],
            "score": item["score"],
        }
        for item in research
    ]

    return {
        "summary": summary,
        "recommendation": recommendation,
        "llm_enabled": False,
        "llm_commentary": "",
        "sections": {
            "technical": indicators,
            "risk": risk,
            "backtest": backtest,
            "research": research,
        },
        "citations": citations,
        "disclaimer": "本报告仅用于研究和学习，不构成任何投资建议。",
    }


def _compact_state_for_llm(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "request": state.get("request", {}),
        "indicators": state.get("indicators", {}),
        "risk": state.get("risk", {}),
        "backtest": state.get("backtest", {}),
        "research": [
            {
                "title": item.get("title"),
                "source": item.get("source"),
                "published_at": item.get("published_at"),
                "doc_type": item.get("doc_type"),
                "content": item.get("content"),
                "sentiment": item.get("sentiment"),
                "score": item.get("score"),
            }
            for item in state.get("research", [])[:5]
        ],
        "rule_report": build_report(state),
    }


def build_llm_report(state: dict[str, Any]) -> dict[str, Any]:
    """Generate a Chinese report with LLM when configured, otherwise return rule report."""
    rule_report = build_report(state)
    if not llm_available():
        return rule_report

    prompt = (
        "你是一个严谨的 A 股量化研究智能体。请基于输入 JSON 生成中文研究报告，"
        "必须比较 backtest.strategies 中各策略的收益、回撤、夏普和胜率，"
        "说明最佳策略是否跑赢买入持有；必须保留可追溯引用，不得编造数据，不得给出确定性投资承诺。"
        "仅输出 JSON，字段包括 summary、recommendation、llm_commentary、key_points、risk_notes。"
        "recommendation 只能是 watchlist_positive、neutral、cautious 三者之一。"
    )
    try:
        llm_result = llm_client.chat_json(prompt, _compact_state_for_llm(state))
    except Exception as exc:
        rule_report["llm_enabled"] = False
        rule_report["llm_error"] = str(exc)
        return rule_report

    summary = str(llm_result.get("summary") or rule_report["summary"])
    recommendation = str(llm_result.get("recommendation") or rule_report["recommendation"])
    if recommendation not in {"watchlist_positive", "neutral", "cautious"}:
        recommendation = rule_report["recommendation"]

    rule_report.update(
        {
            "summary": summary,
            "recommendation": recommendation,
            "llm_enabled": True,
            "llm_commentary": str(llm_result.get("llm_commentary") or ""),
            "key_points": llm_result.get("key_points", []),
            "risk_notes": llm_result.get("risk_notes", []),
        }
    )
    return rule_report


def review_report_with_llm(state: dict[str, Any], rule_review: dict[str, Any]) -> dict[str, Any]:
    if not llm_available():
        return rule_review

    prompt = (
        "你是报告质检智能体。请审查输入中的量化报告是否过度自信、是否缺少引用、"
        "高风险时是否谨慎。仅输出 JSON，字段包括 passed、confidence、issues、suggestions。"
        "confidence 只能是 high、medium、low。issues 和 suggestions 必须是中文字符串数组。"
    )
    payload = {
        "state": _compact_state_for_llm(state),
        "report": state.get("report", {}),
        "rule_review": rule_review,
    }
    try:
        llm_result = llm_client.chat_json(prompt, payload, temperature=0.1)
    except Exception as exc:
        review = dict(rule_review)
        review["llm_enabled"] = False
        review["llm_error"] = str(exc)
        return review

    confidence = str(llm_result.get("confidence") or rule_review.get("confidence", "medium"))
    if confidence not in {"high", "medium", "low"}:
        confidence = str(rule_review.get("confidence", "medium"))

    return {
        "passed": bool(llm_result.get("passed", rule_review.get("passed", False))),
        "issues": llm_result.get("issues", rule_review.get("issues", [])),
        "confidence": confidence,
        "suggestions": llm_result.get("suggestions", []),
        "llm_enabled": True,
    }
