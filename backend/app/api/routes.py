from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.workflow import run_analysis_workflow
from app.models import AnalyzeRequest, AnalyzeResponse, AnalysisSnapshot, RagIngestRequest
from app.services.data_provider import MarketDataProvider
from app.services.rag import ingest_market_doc
from app.services.store import analysis_store

router = APIRouter(prefix="/api")


def _serialize_request(request: AnalyzeRequest) -> dict[str, Any]:
    payload = request.model_dump()
    payload["start_date"] = request.start_date.isoformat()
    payload["end_date"] = request.end_date.isoformat()
    return payload


def _run_background_analysis(run_id: str, request: dict[str, Any]) -> None:
    analysis_store.set_status(run_id, "running")

    def emit(agent: str, status: str, message: str, payload: dict[str, Any] | None = None) -> None:
        analysis_store.add_event(run_id, agent, status, message, payload)

    try:
        result = run_analysis_workflow(request, emit=emit)
        analysis_store.set_result(run_id, result)
    except Exception as exc:
        analysis_store.set_status(run_id, "failed", str(exc))
        analysis_store.add_event(run_id, "Supervisor Agent", "failed", str(exc))


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks) -> AnalyzeResponse:
    payload = _serialize_request(request)
    run_id = analysis_store.create(payload)
    background_tasks.add_task(_run_background_analysis, run_id, payload)
    return AnalyzeResponse(run_id=run_id, status="queued")


@router.get("/analysis/{run_id}", response_model=AnalysisSnapshot)
def get_analysis(run_id: str) -> AnalysisSnapshot:
    snapshot = analysis_store.get(run_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="analysis run not found")
    return AnalysisSnapshot(**snapshot)


@router.get("/analysis/{run_id}/events")
async def analysis_events(run_id: str) -> StreamingResponse:
    if not analysis_store.get(run_id):
        raise HTTPException(status_code=404, detail="analysis run not found")

    async def event_stream():
        cursor = 0
        while True:
            snapshot = analysis_store.get(run_id)
            if not snapshot:
                break

            events = snapshot["events"]
            for event in events[cursor:]:
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            cursor = len(events)

            if snapshot["status"] in {"completed", "failed"} and cursor >= len(events):
                yield f"event: done\ndata: {json.dumps({'status': snapshot['status']})}\n\n"
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/stocks/search")
def search_stocks(q: str = "") -> dict[str, list[dict[str, str]]]:
    provider = MarketDataProvider()
    return {"items": provider.search_stocks(q)}


@router.post("/rag/ingest")
def rag_ingest(request: RagIngestRequest) -> dict:
    return ingest_market_doc(
        symbol=request.symbol,
        title=request.title,
        source=request.source,
        doc_type=request.doc_type,
        content=request.content,
    )
