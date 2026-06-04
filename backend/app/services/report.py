from __future__ import annotations


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
        f"均线交叉策略在区间内回测收益为 {strategy_return:.2%}，"
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
        "sections": {
            "technical": indicators,
            "risk": risk,
            "backtest": backtest,
            "research": research,
        },
        "citations": citations,
        "disclaimer": "本报告仅用于研究和学习，不构成任何投资建议。",
    }
