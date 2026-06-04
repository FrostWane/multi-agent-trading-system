from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from math import sqrt
import re
from typing import Iterable
from uuid import uuid5, NAMESPACE_URL

from app.core.config import settings


@dataclass
class ResearchDocument:
    symbol: str
    title: str
    source: str
    published_at: str
    doc_type: str
    content: str
    sentiment: str = "neutral"


SAMPLE_DOCUMENTS = [
    ResearchDocument(
        symbol="000001",
        title="平安银行零售业务修复跟踪",
        source="sample-research",
        published_at="2024-08-12",
        doc_type="research_note",
        content="零售业务风险出清后，净息差压力仍在，但资产质量边际改善。",
        sentiment="neutral",
    ),
    ResearchDocument(
        symbol="600519",
        title="贵州茅台渠道库存观察",
        source="sample-research",
        published_at="2024-09-02",
        doc_type="research_note",
        content="高端白酒需求韧性仍强，渠道库存和批价波动是主要跟踪变量。",
        sentiment="neutral",
    ),
    ResearchDocument(
        symbol="300750",
        title="动力电池行业价格竞争风险",
        source="sample-news",
        published_at="2024-07-20",
        doc_type="news",
        content="动力电池产业链价格竞争加剧，毛利率承压，需要关注海外订单兑现。",
        sentiment="negative",
    ),
]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text.lower())


def _vectorize(tokens: Iterable[str]) -> dict[str, float]:
    vector: dict[str, float] = {}
    for token in tokens:
        vector[token] = vector.get(token, 0) + 1.0
    return vector


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[key] * right[key] for key in shared)
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


class LocalRAGStore:
    """Small in-memory RAG store used when Qdrant is unavailable."""

    def __init__(self) -> None:
        self._documents: list[ResearchDocument] = list(SAMPLE_DOCUMENTS)

    def ingest(self, document: ResearchDocument) -> dict:
        self._documents.append(document)
        return {"status": "ingested", "count": len(self._documents), "document": asdict(document)}

    def search(self, symbol: str, query: str, limit: int = 5) -> list[dict]:
        query_vector = _vectorize(_tokens(query))
        scored: list[tuple[float, ResearchDocument]] = []
        for document in self._documents:
            symbol_bonus = 0.35 if document.symbol == symbol else 0.0
            doc_vector = _vectorize(_tokens(f"{document.title} {document.content}"))
            score = _cosine(query_vector, doc_vector) + symbol_bonus
            scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                **asdict(document),
                "score": round(score, 4),
            }
            for score, document in scored[:limit]
            if score > 0
        ]


VECTOR_SIZE = 64


def _embed_text(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in _tokens(text):
        bucket = sum(ord(ch) for ch in token) % VECTOR_SIZE
        vector[bucket] += 1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class QdrantRAGStore(LocalRAGStore):
    """Qdrant-backed store with local fallback for offline demos."""

    def __init__(self) -> None:
        super().__init__()
        self._ready = False
        self._client = None
        self._models = None
        try:
            from qdrant_client import QdrantClient, models  # type: ignore

            self._client = QdrantClient(url=settings.qdrant_url, timeout=1.0)
            self._models = models
            self._ensure_collection()
            for document in SAMPLE_DOCUMENTS:
                self._upsert_qdrant(document)
            self._ready = True
        except Exception:
            self._ready = False

    def _ensure_collection(self) -> None:
        assert self._client is not None
        assert self._models is not None
        collections = self._client.get_collections().collections
        names = {collection.name for collection in collections}
        if settings.qdrant_collection not in names:
            self._client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=self._models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=self._models.Distance.COSINE,
                ),
            )

    def _upsert_qdrant(self, document: ResearchDocument) -> None:
        assert self._client is not None
        assert self._models is not None
        payload = asdict(document)
        point_id = str(uuid5(NAMESPACE_URL, f"{document.symbol}:{document.title}:{document.source}"))
        self._client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                self._models.PointStruct(
                    id=point_id,
                    vector=_embed_text(f"{document.title} {document.content}"),
                    payload=payload,
                )
            ],
        )

    def ingest(self, document: ResearchDocument) -> dict:
        local_result = super().ingest(document)
        if self._ready:
            try:
                self._upsert_qdrant(document)
                local_result["vector_db"] = "qdrant"
            except Exception:
                local_result["vector_db"] = "local-fallback"
        else:
            local_result["vector_db"] = "local-fallback"
        return local_result

    def search(self, symbol: str, query: str, limit: int = 5) -> list[dict]:
        if not self._ready or self._client is None or self._models is None:
            return super().search(symbol, query, limit)
        try:
            hits = self._client.search(
                collection_name=settings.qdrant_collection,
                query_vector=_embed_text(query),
                query_filter=self._models.Filter(
                    should=[
                        self._models.FieldCondition(
                            key="symbol",
                            match=self._models.MatchValue(value=symbol),
                        )
                    ]
                ),
                limit=limit,
            )
            results = []
            for hit in hits:
                payload = dict(hit.payload or {})
                payload["score"] = round(float(hit.score), 4)
                results.append(payload)
            return results or super().search(symbol, query, limit)
        except Exception:
            return super().search(symbol, query, limit)


rag_store = QdrantRAGStore()


def search_market_docs(symbol: str, query: str, limit: int = 5) -> list[dict]:
    return rag_store.search(symbol=symbol, query=query, limit=limit)


def ingest_market_doc(
    symbol: str,
    title: str,
    source: str,
    doc_type: str,
    content: str,
) -> dict:
    document = ResearchDocument(
        symbol=symbol,
        title=title,
        source=source,
        published_at=date.today().isoformat(),
        doc_type=doc_type,
        content=content,
    )
    return rag_store.ingest(document)
