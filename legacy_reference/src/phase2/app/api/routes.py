from fastapi import APIRouter, HTTPException

from ..schemas import RecommendationRequest, RecommendationResponse
from ..services.filter_service import filter_restaurants, rank_filtered_restaurants
from ..services.ingestion_service import get_processed_restaurants
from ..services.llm_service import generate_recommendations_with_llm

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    try:
        restaurants_df = get_processed_restaurants()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Data load failed: {exc}") from exc

    filtered = filter_restaurants(restaurants_df, request)
    if filtered.empty:
        return RecommendationResponse(
            total_candidates=0,
            returned_recommendations=0,
            recommendations=[],
        )

    ranked = rank_filtered_restaurants(filtered, request, top_k=20)
    recommendations = generate_recommendations_with_llm(request, ranked)
    return RecommendationResponse(
        total_candidates=len(ranked),
        returned_recommendations=len(recommendations),
        recommendations=recommendations,
    )
