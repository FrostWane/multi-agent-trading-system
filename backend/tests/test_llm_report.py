from app.services import report


def _state():
    return {
        "request": {
            "symbol": "000001",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "horizon": "1m",
            "risk_preference": "balanced",
        },
        "indicators": {"trend": "bullish", "annualized_volatility": 0.18, "max_drawdown": -0.08},
        "risk": {"level": "medium", "score": 55, "reasons": ["年化波动率 18.00%"]},
        "backtest": {"total_return": 0.08, "benchmark_return": 0.03},
        "research": [
            {
                "title": "平安银行零售业务修复跟踪",
                "source": "sample",
                "published_at": "2024-08-12",
                "doc_type": "research_note",
                "content": "零售业务修复，资产质量边际改善。",
                "sentiment": "neutral",
                "score": 0.8,
            }
        ],
    }


def test_build_llm_report_falls_back_without_key(monkeypatch):
    monkeypatch.setattr(report, "llm_available", lambda: False)
    result = report.build_llm_report(_state())
    assert result["llm_enabled"] is False
    assert result["summary"]


def test_build_llm_report_uses_openai_compatible_client(monkeypatch):
    monkeypatch.setattr(report, "llm_available", lambda: True)
    monkeypatch.setattr(
        report.llm_client,
        "chat_json",
        lambda *args, **kwargs: {
            "summary": "大模型生成的中文摘要",
            "recommendation": "neutral",
            "llm_commentary": "证据与量化指标基本一致。",
            "key_points": ["趋势偏强", "风险中等"],
            "risk_notes": ["注意回撤"],
        },
    )
    result = report.build_llm_report(_state())
    assert result["llm_enabled"] is True
    assert result["summary"] == "大模型生成的中文摘要"
    assert result["key_points"] == ["趋势偏强", "风险中等"]


def test_review_report_with_llm_uses_model_feedback(monkeypatch):
    monkeypatch.setattr(report, "llm_available", lambda: True)
    monkeypatch.setattr(
        report.llm_client,
        "chat_json",
        lambda *args, **kwargs: {
            "passed": True,
            "confidence": "medium",
            "issues": [],
            "suggestions": ["补充更多公告引用"],
        },
    )
    state = _state()
    state["report"] = report.build_report(state)
    result = report.review_report_with_llm(
        state,
        {"passed": True, "issues": [], "confidence": "high", "llm_enabled": False},
    )
    assert result["llm_enabled"] is True
    assert result["confidence"] == "medium"
    assert result["suggestions"] == ["补充更多公告引用"]
