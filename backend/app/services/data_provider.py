from __future__ import annotations

from datetime import date
from typing import Any

from app.core.config import settings
from app.services.sample_data import SAMPLE_STOCKS, generate_sample_history


class MarketDataProvider:
    """A-share data adapter with AkShare primary and deterministic sample fallback."""

    def get_stock_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        if settings.data_provider.lower() == "akshare":
            try:
                return self._get_akshare_history(symbol, start_date, end_date)
            except Exception:
                if not settings.use_sample_data_fallback:
                    raise
        return generate_sample_history(symbol, start_date, end_date)

    def _get_akshare_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        import akshare as ak  # type: ignore

        frame = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=str(start_date).replace("-", ""),
            end_date=str(end_date).replace("-", ""),
            adjust="qfq",
        )
        if frame.empty:
            raise ValueError(f"No AkShare data returned for {symbol}")

        rows: list[dict[str, Any]] = []
        for _, row in frame.iterrows():
            rows.append(
                {
                    "date": str(row["日期"]),
                    "open": float(row["开盘"]),
                    "high": float(row["最高"]),
                    "low": float(row["最低"]),
                    "close": float(row["收盘"]),
                    "volume": float(row["成交量"]),
                }
            )
        return rows

    def search_stocks(self, query: str) -> list[dict[str, str]]:
        normalized = query.strip().lower()
        if not normalized:
            return SAMPLE_STOCKS

        matches = [
            stock
            for stock in SAMPLE_STOCKS
            if normalized in stock["symbol"].lower() or normalized in stock["name"].lower()
        ]
        return matches[:10]
