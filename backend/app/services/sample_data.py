from __future__ import annotations

from datetime import date, datetime, timedelta
import math
import random


def _to_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def generate_sample_history(
    symbol: str = "000001",
    start_date: str | date = "2024-01-01",
    end_date: str | date = "2024-12-31",
) -> list[dict[str, float | str]]:
    """Generate deterministic OHLCV data for demos and tests."""
    start = _to_date(start_date)
    end = _to_date(end_date)
    seed = sum(ord(ch) for ch in symbol)
    rng = random.Random(seed)
    price = 10 + (seed % 50)
    rows: list[dict[str, float | str]] = []

    current = start
    index = 0
    while current <= end:
        if current.weekday() < 5:
            drift = 0.0008 * math.sin(index / 9)
            shock = rng.uniform(-0.018, 0.018)
            open_price = price * (1 + rng.uniform(-0.006, 0.006))
            close = max(1, price * (1 + drift + shock))
            high = max(open_price, close) * (1 + rng.uniform(0.001, 0.018))
            low = min(open_price, close) * (1 - rng.uniform(0.001, 0.018))
            volume = 800_000 + int(abs(shock) * 80_000_000) + rng.randint(0, 350_000)
            rows.append(
                {
                    "date": current.isoformat(),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": float(volume),
                }
            )
            price = close
            index += 1
        current += timedelta(days=1)
    return rows


SAMPLE_STOCKS = [
    {"symbol": "000001", "name": "平安银行", "market": "SZ"},
    {"symbol": "000002", "name": "万科A", "market": "SZ"},
    {"symbol": "600519", "name": "贵州茅台", "market": "SH"},
    {"symbol": "600036", "name": "招商银行", "market": "SH"},
    {"symbol": "300750", "name": "宁德时代", "market": "SZ"},
    {"symbol": "601318", "name": "中国平安", "market": "SH"},
]
