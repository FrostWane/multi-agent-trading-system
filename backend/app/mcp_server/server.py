from __future__ import annotations

from typing import Optional

from app.services.backtest import run_moving_average_backtest, run_strategy_comparison
from app.services.data_provider import MarketDataProvider
from app.services.indicators import summarize_indicators
from app.services.rag import search_market_docs
from app.services.risk import assess_risk


try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - helpful when dependencies are not installed yet
    FastMCP = None  # type: ignore


if FastMCP is not None:
    mcp = FastMCP("multi-agent-trading-tools")

    @mcp.tool()
    def get_stock_history(symbol: str, start_date: str, end_date: str) -> list[dict]:
        """Fetch A-share OHLCV history using AkShare with sample fallback."""
        return MarketDataProvider().get_stock_history(symbol, start_date, end_date)

    @mcp.tool()
    def calculate_indicators(history: list[dict]) -> dict:
        """Calculate MA, RSI, MACD, volatility, and drawdown features."""
        return summarize_indicators(history)

    @mcp.tool()
    def search_market_research(symbol: str, query: str, limit: int = 5) -> list[dict]:
        """Search market research evidence from the local RAG store."""
        return search_market_docs(symbol, query, limit)

    @mcp.tool()
    def run_backtest(history: list[dict]) -> dict:
        """Run the default moving-average crossover backtest."""
        return run_moving_average_backtest(history)

    @mcp.tool()
    def compare_backtest_strategies(history: list[dict], config: Optional[dict] = None) -> dict:
        """Compare buy-hold, MA crossover, momentum, and RSI reversal strategies."""
        return run_strategy_comparison(history, config or {})

    @mcp.tool()
    def generate_risk_profile(indicators: dict, research: list[dict], preference: str = "balanced") -> dict:
        """Score market, technical, and research risk for a symbol."""
        return assess_risk(indicators, research, preference)


def main() -> None:
    if FastMCP is None:
        raise RuntimeError("Install backend dependencies to run the MCP server.")
    mcp.run()


if __name__ == "__main__":
    main()
