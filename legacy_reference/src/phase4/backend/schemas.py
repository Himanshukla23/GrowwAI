from __future__ import annotations

from typing import List

from pydantic import BaseModel

from src.phase2.app.schemas import RecommendationItem, RecommendationRequest


class Phase4RecommendResponse(BaseModel):
    request_id: str
    total_candidates: int
    returned_recommendations: int
    processing_ms: int
    recommendations: List[RecommendationItem]


class Phase4BatchRequest(BaseModel):
    requests: List[RecommendationRequest]


class Phase4BatchItem(BaseModel):
    request_index: int
    request_id: str
    total_candidates: int
    returned_recommendations: int
    recommendations: List[RecommendationItem]


class Phase4BatchResponse(BaseModel):
    batch_size: int
    processing_ms: int
    results: List[Phase4BatchItem]


class Phase4ExplainResponse(BaseModel):
    request_id: str
    filtering_summary: dict
    ranking_summary: dict
    llm_summary: dict
    processing_ms: int
