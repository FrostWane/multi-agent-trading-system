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

    summary = (
        f"{request['symbol']} shows {trend} technical momentum with {risk_level} risk. "
        f"The MA crossover backtest returned {strategy_return:.2%}, versus "
        f"{benchmark_return:.2%} buy-and-hold over the same period."
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
        "disclaimer": "This report is for research and education only, not investment advice.",
    }
