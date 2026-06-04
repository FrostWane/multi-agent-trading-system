from app.services.rag import ingest_market_doc, search_market_docs


def test_rag_ingest_and_search_returns_citation_payload():
    ingest_market_doc(
        symbol="000001",
        title="平安银行资本充足率观察",
        source="unit-test",
        doc_type="note",
        content="资本充足率保持稳健，资产质量仍需持续跟踪。",
    )
    results = search_market_docs("000001", "资本充足率 平安银行", limit=3)
    assert results
    assert {"symbol", "title", "source", "published_at", "doc_type", "content"} <= set(results[0])
