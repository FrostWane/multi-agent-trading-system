from app.services.backtest import run_moving_average_backtest
from app.services.sample_data import generate_sample_history


def test_moving_average_backtest_returns_core_metrics():
    history = generate_sample_history("000001", "2024-01-01", "2024-05-31")
    result = run_moving_average_backtest(history)
    assert result["strategy"] == "ma_cross"
    assert "total_return" in result
    assert "benchmark_return" in result
    assert result["trades"] >= 0
