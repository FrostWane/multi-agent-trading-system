from __future__ import annotations

import math
from statistics import mean, pstdev


def _closes(history: list[dict]) -> list[float]:
    return [float(row["close"]) for row in history]


def moving_average(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
        else:
            result.append(round(mean(values[index + 1 - window : index + 1]), 4))
    return result


def exponential_moving_average(values: list[float], window: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (window + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append((value * alpha) + (result[-1] * (1 - alpha)))
    return [round(item, 4) for item in result]


def rsi(values: list[float], window: int = 14) -> float:
    if len(values) <= window:
        return 50.0
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-window - 1 : -1], values[-window:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    average_gain = mean(gains) if gains else 0
    average_loss = mean(losses) if losses else 0
    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return round(100 - (100 / (1 + relative_strength)), 2)


def macd(values: list[float]) -> dict[str, float]:
    if not values:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
    ema12 = exponential_moving_average(values, 12)
    ema26 = exponential_moving_average(values, 26)
    diffs = [fast - slow for fast, slow in zip(ema12, ema26)]
    signal_line = exponential_moving_average(diffs, 9)
    return {
        "macd": round(diffs[-1], 4),
        "signal": round(signal_line[-1], 4),
        "histogram": round(diffs[-1] - signal_line[-1], 4),
    }


def annualized_volatility(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    returns = [(current / previous) - 1 for previous, current in zip(values[:-1], values[1:])]
    return round(pstdev(returns) * math.sqrt(252), 4)


def max_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = (value / peak) - 1
        worst = min(worst, drawdown)
    return round(worst, 4)


def summarize_indicators(history: list[dict]) -> dict:
    closes = _closes(history)
    if not closes:
        return {"trend": "unknown", "latest_close": None}
    ma5 = moving_average(closes, 5)[-1]
    ma20 = moving_average(closes, 20)[-1]
    ma60 = moving_average(closes, 60)[-1]
    latest = closes[-1]
    first = closes[0]
    change = (latest / first) - 1 if first else 0

    if ma20 is None:
        trend = "insufficient_data"
    elif latest > ma20 and (ma60 is None or ma20 > ma60):
        trend = "bullish"
    elif latest < ma20:
        trend = "bearish"
    else:
        trend = "neutral"

    return {
        "latest_close": round(latest, 2),
        "period_return": round(change, 4),
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
        "rsi14": rsi(closes),
        "macd": macd(closes),
        "annualized_volatility": annualized_volatility(closes),
        "max_drawdown": max_drawdown(closes),
        "trend": trend,
    }
