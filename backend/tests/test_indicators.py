from app.services.indicators import annualized_volatility, max_drawdown, moving_average, rsi


def test_moving_average_waits_until_window_is_full():
    assert moving_average([1, 2, 3, 4, 5], 3) == [None, None, 2, 3, 4]


def test_rsi_bounds():
    value = rsi([10, 11, 10, 12, 13, 12, 14, 15, 14, 16, 17, 18, 17, 19, 20])
    assert 0 <= value <= 100


def test_volatility_and_drawdown_are_numeric():
    values = [10, 12, 11, 14, 13]
    assert annualized_volatility(values) > 0
    assert max_drawdown(values) < 0
