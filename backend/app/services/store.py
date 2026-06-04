from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AnalysisStore:
    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def create(self, request: dict[str, Any]) -> str:
        run_id = str(uuid4())
        with self._lock:
            self._runs[run_id] = {
                "run_id": run_id,
                "status": "queued",
                "request": request,
                "events": [],
                "result": None,
                "error": None,
            }
        self.add_event(run_id, "Supervisor Agent", "queued", "分析请求已接收。")
        return run_id

    def set_status(self, run_id: str, status: str, error: str | None = None) -> None:
        with self._lock:
            self._runs[run_id]["status"] = status
            self._runs[run_id]["error"] = error

    def set_result(self, run_id: str, result: dict[str, Any]) -> None:
        with self._lock:
            self._runs[run_id]["result"] = result
            self._runs[run_id]["status"] = "completed"

    def add_event(
        self,
        run_id: str,
        agent: str,
        status: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "run_id": run_id,
            "agent": agent,
            "status": status,
            "message": message,
            "payload": payload or {},
            "created_at": utc_now(),
        }
        with self._lock:
            self._runs[run_id]["events"].append(event)

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            run = self._runs.get(run_id)
            return deepcopy(run) if run else None


analysis_store = AnalysisStore()
