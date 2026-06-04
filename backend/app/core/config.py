from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "market_research")
    data_provider: str = os.getenv("DATA_PROVIDER", "akshare")
    use_sample_data_fallback: bool = os.getenv("USE_SAMPLE_DATA_FALLBACK", "true").lower() == "true"
    cors_origins: tuple[str, ...] = tuple(
        _split_csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"))
    )


settings = Settings()
