from __future__ import annotations


def assess_risk(indicators: dict, research: list[dict], risk_preference: str = "balanced") -> dict:
    volatility = float(indicators.get("annualized_volatility") or 0)
    drawdown = abs(float(indicators.get("max_drawdown") or 0))
    rsi = float(indicators.get("rsi14") or 50)
    negative_hits = sum(1 for item in research if item.get("sentiment") == "negative")

    score = 35
    score += min(30, int(volatility * 100))
    score += min(25, int(drawdown * 120))
    if rsi > 75:
        score += 10
    if rsi < 25:
        score += 8
    score += min(20, negative_hits * 8)

    adjustment = {"conservative": 8, "balanced": 0, "aggressive": -6}.get(risk_preference, 0)
    score = max(0, min(100, score + adjustment))

    if score >= 70:
        level = "high"
    elif score >= 45:
        level = "medium"
    else:
        level = "low"

    reasons = [
        f"annualized volatility {volatility:.2%}",
        f"max drawdown {drawdown:.2%}",
        f"RSI14 {rsi:.2f}",
    ]
    if negative_hits:
        reasons.append(f"{negative_hits} negative research signals")

    return {"score": score, "level": level, "reasons": reasons, "preference": risk_preference}
