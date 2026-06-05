from __future__ import annotations

from contextlib import contextmanager
from datetime import date
import os
from threading import Lock
from typing import Any

from app.core.config import settings
from app.services.sample_data import SAMPLE_STOCKS, generate_sample_history


_AKSHARE_ENV_LOCK = Lock()


@contextmanager
def _akshare_network_env():
    if not settings.akshare_no_proxy:
        yield
        return

    with _AKSHARE_ENV_LOCK:
        import requests

        proxy_keys = (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        )
        old_values = {key: os.environ.get(key) for key in proxy_keys}
        for key in proxy_keys:
            os.environ.pop(key, None)
        os.environ["NO_PROXY"] = "*"
        os.environ["no_proxy"] = "*"
        old_merge_environment_settings = requests.sessions.Session.merge_environment_settings

        def merge_environment_settings_without_proxy(
            session: requests.sessions.Session,
            url: str,
            proxies: dict[str, Any] | None,
            stream: bool | None,
            verify: bool | str | None,
            cert: Any,
        ) -> dict[str, Any]:
            settings = old_merge_environment_settings(session, url, {}, stream, verify, cert)
            settings["proxies"] = {}
            return settings

        requests.sessions.Session.merge_environment_settings = merge_environment_settings_without_proxy
        try:
            yield
        finally:
            requests.sessions.Session.merge_environment_settings = old_merge_environment_settings
            for key, value in old_values.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class MarketDataProvider:
    """A-share data adapter with AkShare primary and deterministic sample fallback."""

    def get_stock_history_with_meta(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> dict[str, Any]:
        if settings.data_provider.lower() == "akshare":
            try:
                return {
                    "rows": self._get_akshare_history(symbol, start_date, end_date),
                    "metadata": {
                        "provider": "akshare",
                        "provider_label": "AkShare",
                        "adjust": "qfq",
                        "adjust_label": "qfq",
                        "is_sample": False,
                    },
                }
            except Exception as exc:
                upstream_errors = [f"AkShare: {type(exc).__name__}: {exc}"]
                try:
                    return {
                        "rows": self._get_eastmoney_history(symbol, start_date, end_date),
                        "metadata": {
                            "provider": "eastmoney",
                            "provider_label": "EastMoney",
                            "adjust": "qfq",
                            "adjust_label": "qfq",
                            "is_sample": False,
                            "fallback_reason": f"AkShare failed; switched to EastMoney direct: {type(exc).__name__}",
                        },
                    }
                except Exception as eastmoney_exc:
                    upstream_errors.append(
                        f"EastMoney: {type(eastmoney_exc).__name__}: {eastmoney_exc}"
                    )
                try:
                    return {
                        "rows": self._get_tencent_history(symbol, start_date, end_date),
                        "metadata": {
                            "provider": "tencent",
                            "provider_label": "Tencent",
                            "adjust": "qfq",
                            "adjust_label": "qfq",
                            "is_sample": False,
                            "fallback_reason": "AkShare/EastMoney failed; switched to Tencent daily history.",
                        },
                    }
                except Exception as tencent_exc:
                    upstream_errors.append(f"Tencent: {type(tencent_exc).__name__}: {tencent_exc}")
                    fallback_reason = "; ".join(upstream_errors)
                if not settings.use_sample_data_fallback:
                    raise
                return {
                    "rows": generate_sample_history(symbol, start_date, end_date),
                    "metadata": {
                        "provider": "sample",
                        "provider_label": "Sample",
                        "adjust": "none",
                        "adjust_label": "none",
                        "is_sample": True,
                        "fallback_reason": fallback_reason,
                    },
                }

        return {
            "rows": generate_sample_history(symbol, start_date, end_date),
            "metadata": {
                "provider": "sample",
                "provider_label": "Sample",
                "adjust": "none",
                "adjust_label": "none",
                "is_sample": True,
            },
        }

    def get_stock_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        return self.get_stock_history_with_meta(symbol, start_date, end_date)["rows"]

    def _get_akshare_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        with _akshare_network_env():
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

    def _get_tencent_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        with _akshare_network_env():
            import akshare as ak  # type: ignore

            frame = ak.stock_zh_a_hist_tx(
                symbol=self._symbol_with_market_prefix(symbol),
                start_date=str(start_date).replace("-", ""),
                end_date=str(end_date).replace("-", ""),
                adjust="qfq",
                timeout=10,
            )
        if frame.empty:
            raise ValueError(f"No Tencent data returned for {symbol}")

        rows: list[dict[str, Any]] = []
        for _, row in frame.iterrows():
            rows.append(
                {
                    "date": str(row["date"])[:10],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["amount"]),
                }
            )
        return rows

    def _get_eastmoney_history(
        self,
        symbol: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        import requests

        market = "1" if symbol.startswith(("5", "6", "9")) else "0"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": "101",
            "fqt": "1",
            "secid": f"{market}.{symbol}",
            "beg": str(start_date).replace("-", ""),
            "end": str(end_date).replace("-", ""),
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            ),
            "Referer": "https://quote.eastmoney.com/",
        }
        with _akshare_network_env():
            response = requests.get(
                "https://push2his.eastmoney.com/api/qt/stock/kline/get",
                params=params,
                headers=headers,
                timeout=10,
                proxies={},
            )
        response.raise_for_status()
        payload = response.json()
        klines = payload.get("data", {}).get("klines") or []
        if not klines:
            raise ValueError(f"No EastMoney data returned for {symbol}")

        rows: list[dict[str, Any]] = []
        for line in klines:
            fields = line.split(",")
            rows.append(
                {
                    "date": fields[0],
                    "open": float(fields[1]),
                    "close": float(fields[2]),
                    "high": float(fields[3]),
                    "low": float(fields[4]),
                    "volume": float(fields[5]),
                }
            )
        return rows

    def _symbol_with_market_prefix(self, symbol: str) -> str:
        market = "sh" if symbol.startswith(("5", "6", "9")) else "sz"
        return f"{market}{symbol}"

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
