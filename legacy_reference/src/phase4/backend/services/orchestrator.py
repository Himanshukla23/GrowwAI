from __future__ import annotations

import time
import uuid
from typing import Any

from src.phase2.app.schemas import RecommendationRequest
from src.phase2.app.services.filter_service import filter_restaurants, rank_filtered_restaurants
from src.phase3.database import get_all_restaurants
from src.phase3.services.async_llm_service import generate_recommendations_with_llm_async

from .audit_service import write_audit_log


def _request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


async def run_recommendation_pipeline(request: RecommendationRequest) -> dict[str, Any]:
    start = time.perf_counter()
    req_id = _request_id()

    restaurants_df = get_all_restaurants()
    filtered = filter_restaurants(restaurants_df, request)
    if filtered.empty:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        payload = {
            "request_id": req_id,
            "total_candidates": 0,
            "returned_recommendations": 0,
            "processing_ms": elapsed_ms,
            "recommendations": [],
        }
        write_audit_log(
            {
                "request_id": req_id,
                "status": "ok",
                "total_candidates": 0,
                "returned_recommendations": 0,
                "processing_ms": elapsed_ms,
            }
        )
        return payload

    ranked = rank_filtered_restaurants(filtered, request, top_k=20)
    recommendations = await generate_recommendations_with_llm_async(request, ranked)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    payload = {
        "request_id": req_id,
        "total_candidates": len(ranked),
        "returned_recommendations": len(recommendations),
        "processing_ms": elapsed_ms,
        "recommendations": recommendations,
    }

    write_audit_log(
        {
            "request_id": req_id,
            "status": "ok",
            "total_candidates": len(ranked),
            "returned_recommendations": len(recommendations),
            "processing_ms": elapsed_ms,
        }
    )
    return payload


async def run_explain_pipeline(request: RecommendationRequest) -> dict[str, Any]:
    start = time.perf_counter()
    req_id = _request_id()

    restaurants_df = get_all_restaurants()
    filtered = filter_restaurants(restaurants_df, request)
    ranked = rank_filtered_restaurants(filtered, request, top_k=20) if not filtered.empty else filtered
    llm_recs = await generate_recommendations_with_llm_async(request, ranked) if not ranked.empty else []
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    ranking_preview = []
    if not ranked.empty:
        preview_cols = ["name", "rating", "cost"]
        ranking_preview = ranked[preview_cols].head(5).to_dict(orient="records")

    write_audit_log(
        {
            "request_id": req_id,
            "status": "ok",
            "mode": "explain",
            "filtered_count": int(len(filtered)),
            "ranked_count": int(len(ranked)),
            "llm_count": int(len(llm_recs)),
            "processing_ms": elapsed_ms,
        }
    )

    return {
        "request_id": req_id,
        "filtering_summary": {
            "input_count": int(len(restaurants_df)),
            "filtered_count": int(len(filtered)),
        },
        "ranking_summary": {
            "ranked_count": int(len(ranked)),
            "top_preview": ranking_preview,
        },
        "llm_summary": {
            "returned_recommendations": int(len(llm_recs)),
            "llm_input_cap": 20,
            "filter_before_llm_enforced": True,
        },
        "processing_ms": elapsed_ms,
    }
