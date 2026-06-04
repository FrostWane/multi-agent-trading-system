from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings


def llm_available() -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key != "replace-me")


class LLMError(RuntimeError):
    pass


class OpenAICompatibleLLM:
    """Minimal OpenAI-compatible chat client with no hard SDK dependency."""

    def __init__(self) -> None:
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        self.timeout = settings.llm_timeout_seconds

    def chat_json(
        self,
        system_prompt: str,
        user_payload: dict[str, Any],
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        if not llm_available():
            raise LLMError("未配置大模型 API Key")

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise LLMError(f"大模型请求失败：{response.status_code} {response.text[:300]}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError(f"大模型未返回合法 JSON：{content[:300]}") from exc


llm_client = OpenAICompatibleLLM()
