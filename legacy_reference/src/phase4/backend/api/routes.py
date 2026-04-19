from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from src.phase2.app.schemas import RecommendationRequest

from ..schemas import (
    Phase4BatchItem,
    Phase4BatchRequest,
    Phase4BatchResponse,
    Phase4ExplainResponse,
    Phase4RecommendResponse,
)
from ..services.orchestrator import run_explain_pipeline, run_recommendation_pipeline

router = APIRouter(prefix="/phase4", tags=["phase4-backend"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "phase": "phase4-backend"}


@router.post("/recommend", response_model=Phase4RecommendResponse)
async def recommend(request: RecommendationRequest) -> Phase4RecommendResponse:
    try:
        payload = await run_recommendation_pipeline(request)
        return Phase4RecommendResponse(**payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Phase4 recommend failed: {exc}") from exc


@router.post("/recommend/explain", response_model=Phase4ExplainResponse)
async def explain(request: RecommendationRequest) -> Phase4ExplainResponse:
    try:
        payload = await run_explain_pipeline(request)
        return Phase4ExplainResponse(**payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Phase4 explain failed: {exc}") from exc


@router.post("/recommend/batch", response_model=Phase4BatchResponse)
async def batch_recommend(batch: Phase4BatchRequest) -> Phase4BatchResponse:
    start = time.perf_counter()
    items: list[Phase4BatchItem] = []

    for idx, request in enumerate(batch.requests):
        try:
            payload = await run_recommendation_pipeline(request)
            items.append(
                Phase4BatchItem(
                    request_index=idx,
                    request_id=payload["request_id"],
                    total_candidates=payload["total_candidates"],
                    returned_recommendations=payload["returned_recommendations"],
                    recommendations=payload["recommendations"],
                )
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Batch item {idx} failed: {exc}") from exc

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return Phase4BatchResponse(batch_size=len(batch.requests), processing_ms=elapsed_ms, results=items)
