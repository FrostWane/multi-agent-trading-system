from app.services.backtest import run_moving_average_backtest, run_strategy_comparison
from app.services.sample_data import generate_sample_history


def test_moving_average_backtest_returns_core_metrics():
    history = generate_sample_history("000001", "2024-01-01", "2024-05-31")
    result = run_moving_average_backtest(history)
    assert result["strategy"] == "ma_cross"
    assert "total_return" in result
    assert "benchmark_return" in result
    assert result["trades"] >= 0


def test_strategy_comparison_returns_multiple_strategies():
    history = generate_sample_history("000001", "2024-01-01", "2024-08-31")
    result = run_strategy_comparison(
        history,
        {
            "strategy_set": "compare_all",
            "short_window": 5,
            "long_window": 20,
            "momentum_window": 15,
            "rsi_window": 14,
            "initial_cash": 100000,
            "fee_rate": 0.0003,
        },
    )
    strategies = {item["strategy"] for item in result["strategies"]}
    assert {"buy_hold", "ma_cross", "momentum", "rsi_reversal"} <= strategies
    assert result["best_strategy"] in strategies
    assert result["equity_curve"]
    assert "sharpe" in result
