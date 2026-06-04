from __future__ import annotations

from app.services.indicators import moving_average


def run_moving_average_backtest(
    history: list[dict],
    short_window: int = 5,
    long_window: int = 20,
) -> dict:
    closes = [float(row["close"]) for row in history]
    if len(closes) <= long_window:
        return {
            "strategy": "ma_cross",
            "total_return": 0.0,
            "benchmark_return": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "trades": 0,
        }

    short_ma = moving_average(closes, short_window)
    long_ma = moving_average(closes, long_window)
    equity = 1.0
    position = 0
    trades = 0
    wins = 0
    entry_price = 0.0
    curve = [equity]

    for index in range(1, len(closes)):
        if short_ma[index] is None or long_ma[index] is None:
            curve.append(equity)
            continue

        bullish = float(short_ma[index]) > float(long_ma[index])
        bearish = float(short_ma[index]) < float(long_ma[index])

        if bullish and position == 0:
            position = 1
            entry_price = closes[index]
            trades += 1
        elif bearish and position == 1:
            trade_return = (closes[index] / entry_price) - 1
            equity *= 1 + trade_return
            wins += int(trade_return > 0)
            position = 0
        curve.append(equity * (closes[index] / entry_price if position else 1))

    if position == 1 and entry_price:
        trade_return = (closes[-1] / entry_price) - 1
        equity *= 1 + trade_return
        wins += int(trade_return > 0)

    peak = curve[0]
    worst = 0.0
    for value in curve:
        peak = max(peak, value)
        worst = min(worst, (value / peak) - 1)

    benchmark = (closes[-1] / closes[0]) - 1
    return {
        "strategy": "ma_cross",
        "parameters": {"short_window": short_window, "long_window": long_window},
        "total_return": round(equity - 1, 4),
        "benchmark_return": round(benchmark, 4),
        "max_drawdown": round(worst, 4),
        "win_rate": round(wins / trades, 4) if trades else 0.0,
        "trades": trades,
    }
