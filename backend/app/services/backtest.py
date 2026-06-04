from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Any

from app.services.indicators import moving_average, rsi


DEFAULT_BACKTEST_CONFIG = {
    "strategy_set": "compare_all",
    "short_window": 5,
    "long_window": 20,
    "momentum_window": 20,
    "rsi_window": 14,
    "rsi_buy_threshold": 30,
    "rsi_sell_threshold": 70,
    "initial_cash": 100000.0,
    "fee_rate": 0.0003,
}

STRATEGY_LABELS = {
    "buy_hold": "买入持有",
    "ma_cross": "均线交叉",
    "momentum": "动量策略",
    "rsi_reversal": "RSI 反转",
}


def _closes(history: list[dict]) -> list[float]:
    return [float(row["close"]) for row in history]


def _dates(history: list[dict]) -> list[str]:
    return [str(row["date"]) for row in history]


def _max_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return round(worst, 4)


def _sharpe(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    returns = [(current / previous) - 1 for previous, current in zip(values[:-1], values[1:]) if previous]
    if len(returns) < 2:
        return 0.0
    deviation = pstdev(returns)
    if deviation == 0:
        return 0.0
    return round((mean(returns) / deviation) * math.sqrt(252), 4)


def _annualized_return(total_return: float, periods: int) -> float:
    if periods <= 1:
        return round(total_return, 4)
    years = periods / 252
    if years <= 0:
        return round(total_return, 4)
    return round((1 + total_return) ** (1 / years) - 1, 4)


def _empty_result(strategy: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "strategy": strategy,
        "label": STRATEGY_LABELS.get(strategy, strategy),
        "parameters": parameters,
        "total_return": 0.0,
        "annualized_return": 0.0,
        "benchmark_return": 0.0,
        "max_drawdown": 0.0,
        "sharpe": 0.0,
        "win_rate": 0.0,
        "trades": 0,
        "final_equity": float(parameters.get("initial_cash", 100000.0)),
        "equity_curve": [],
    }


def _simulate_signals(
    history: list[dict],
    signals: list[int],
    strategy: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    closes = _closes(history)
    dates = _dates(history)
    initial_cash = float(parameters.get("initial_cash", 100000.0))
    fee_rate = float(parameters.get("fee_rate", 0.0003))

    if len(closes) < 2:
        return _empty_result(strategy, parameters)

    cash = initial_cash
    shares = 0.0
    entry_value = 0.0
    trades = 0
    closed_trades = 0
    wins = 0
    equity_values: list[float] = []
    equity_curve: list[dict[str, float | str]] = []
    benchmark_start = closes[0]

    for index, close in enumerate(closes):
        target = signals[index]
        equity_before_trade = cash + shares * close

        if target == 1 and shares == 0 and cash > 0:
            entry_value = equity_before_trade
            shares = (cash * (1 - fee_rate)) / close
            cash = 0.0
            trades += 1
        elif target == 0 and shares > 0:
            cash = shares * close * (1 - fee_rate)
            trade_return = cash / entry_value - 1 if entry_value else 0.0
            wins += int(trade_return > 0)
            closed_trades += 1
            shares = 0.0
            entry_value = 0.0

        equity = cash + shares * close
        benchmark_equity = initial_cash * (close / benchmark_start)
        equity_values.append(equity)
        equity_curve.append(
            {
                "date": dates[index],
                "equity": round(equity, 2),
                "benchmark": round(benchmark_equity, 2),
            }
        )

    if shares > 0 and entry_value:
        final_cash = shares * closes[-1] * (1 - fee_rate)
        trade_return = final_cash / entry_value - 1
        wins += int(trade_return > 0)
        closed_trades += 1

    final_equity = equity_values[-1]
    total_return = final_equity / initial_cash - 1
    benchmark_return = closes[-1] / closes[0] - 1

    return {
        "strategy": strategy,
        "label": STRATEGY_LABELS.get(strategy, strategy),
        "parameters": parameters,
        "total_return": round(total_return, 4),
        "annualized_return": _annualized_return(total_return, len(closes)),
        "benchmark_return": round(benchmark_return, 4),
        "max_drawdown": _max_drawdown(equity_values),
        "sharpe": _sharpe(equity_values),
        "win_rate": round(wins / closed_trades, 4) if closed_trades else 0.0,
        "trades": trades,
        "final_equity": round(final_equity, 2),
        "equity_curve": equity_curve,
    }


def _buy_hold(history: list[dict], config: dict[str, Any]) -> dict[str, Any]:
    closes = _closes(history)
    signals = [1 for _ in closes]
    result = _simulate_signals(history, signals, "buy_hold", config)
    result["trades"] = 1 if len(closes) > 1 else 0
    result["win_rate"] = 1.0 if result["total_return"] > 0 else 0.0
    return result


def _ma_cross_signals(history: list[dict], config: dict[str, Any]) -> list[int]:
    closes = _closes(history)
    short_window = int(config["short_window"])
    long_window = int(config["long_window"])
    short_ma = moving_average(closes, short_window)
    long_ma = moving_average(closes, long_window)
    signals: list[int] = []
    for index in range(len(closes)):
        if short_ma[index] is None or long_ma[index] is None:
            signals.append(0)
        else:
            signals.append(1 if float(short_ma[index]) > float(long_ma[index]) else 0)
    return signals


def _momentum_signals(history: list[dict], config: dict[str, Any]) -> list[int]:
    closes = _closes(history)
    window = int(config["momentum_window"])
    signals: list[int] = []
    for index, close in enumerate(closes):
        if index < window:
            signals.append(0)
        else:
            signals.append(1 if close > closes[index - window] else 0)
    return signals


def _rsi_reversal_signals(history: list[dict], config: dict[str, Any]) -> list[int]:
    closes = _closes(history)
    window = int(config["rsi_window"])
    buy_threshold = float(config["rsi_buy_threshold"])
    sell_threshold = float(config["rsi_sell_threshold"])
    signals: list[int] = []
    position = 0

    for index in range(len(closes)):
        if index <= window:
            signals.append(position)
            continue
        current_rsi = rsi(closes[: index + 1], window)
        if current_rsi <= buy_threshold:
            position = 1
        elif current_rsi >= sell_threshold:
            position = 0
        signals.append(position)
    return signals


def _normalize_config(config: dict[str, Any] | None) -> dict[str, Any]:
    merged = {**DEFAULT_BACKTEST_CONFIG, **(config or {})}
    merged["short_window"] = max(2, int(merged["short_window"]))
    merged["long_window"] = max(merged["short_window"] + 1, int(merged["long_window"]))
    merged["momentum_window"] = max(2, int(merged["momentum_window"]))
    merged["rsi_window"] = max(2, int(merged["rsi_window"]))
    merged["rsi_buy_threshold"] = float(merged["rsi_buy_threshold"])
    merged["rsi_sell_threshold"] = float(merged["rsi_sell_threshold"])
    merged["initial_cash"] = max(1000.0, float(merged["initial_cash"]))
    merged["fee_rate"] = max(0.0, float(merged["fee_rate"]))
    return merged


def run_strategy_comparison(history: list[dict], config: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = _normalize_config(config)
    strategy_set = str(normalized.get("strategy_set", "compare_all"))
    strategy_names = (
        ["ma_cross", "momentum", "rsi_reversal"]
        if strategy_set == "compare_all"
        else [strategy_set if strategy_set in {"ma_cross", "momentum", "rsi_reversal"} else "ma_cross"]
    )

    strategy_results = [_buy_hold(history, normalized)]
    signal_builders = {
        "ma_cross": _ma_cross_signals,
        "momentum": _momentum_signals,
        "rsi_reversal": _rsi_reversal_signals,
    }

    for strategy in strategy_names:
        signals = signal_builders[strategy](history, normalized)
        strategy_results.append(_simulate_signals(history, signals, strategy, normalized))

    candidates = [item for item in strategy_results if item["strategy"] != "buy_hold"]
    best = max(candidates or strategy_results, key=lambda item: item["total_return"])
    benchmark = strategy_results[0]

    return {
        "strategy": best["strategy"],
        "strategy_label": best["label"],
        "best_strategy": best["strategy"],
        "best_strategy_label": best["label"],
        "selected_strategy": strategy_set,
        "parameters": normalized,
        "total_return": best["total_return"],
        "annualized_return": best["annualized_return"],
        "benchmark_return": benchmark["total_return"],
        "max_drawdown": best["max_drawdown"],
        "sharpe": best["sharpe"],
        "win_rate": best["win_rate"],
        "trades": best["trades"],
        "final_equity": best["final_equity"],
        "equity_curve": best["equity_curve"],
        "strategies": strategy_results,
    }


def run_moving_average_backtest(
    history: list[dict],
    short_window: int = 5,
    long_window: int = 20,
) -> dict[str, Any]:
    comparison = run_strategy_comparison(
        history,
        {
            "strategy_set": "ma_cross",
            "short_window": short_window,
            "long_window": long_window,
        },
    )
    ma_result = next(item for item in comparison["strategies"] if item["strategy"] == "ma_cross")
    return {
        **ma_result,
        "benchmark_return": comparison["benchmark_return"],
        "strategies": comparison["strategies"],
        "equity_curve": ma_result["equity_curve"],
    }
