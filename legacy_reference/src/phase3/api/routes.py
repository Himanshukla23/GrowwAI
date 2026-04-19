from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
import time
import uuid
from typing import Optional

from src.phase2.app.schemas import RecommendationRequest, RecommendationResponse
from src.phase2.app.services.filter_service import filter_restaurants, rank_filtered_restaurants
from src.phase2.app.services.ingestion_service import get_processed_restaurants

# Phase 3 imports
from ..database import get_stats, upsert_restaurants, get_all_restaurants, get_unique_locations, get_unique_cuisines
from ..services.token_tracker import tracker
from ..services.async_llm_service import generate_recommendations_with_llm_async
from ..logging_config import logger

router = APIRouter(prefix="/phase3", tags=["phase3-backend"])

@router.get("/health")
def health():
    """Enhanced health check with DB and token stats."""
    db_stats = get_stats()
    token_stats = tracker.get_usage_stats()
    
    status = "ok"
    if db_stats["status"] != "online":
        status = "degraded"
        
    return {
        "status": status,
        "database": db_stats,
        "token_budget": token_stats,
        "timestamp": time.time()
    }

@router.get("/metrics")
def metrics():
    """Expose metrics for observability."""
    return {
        "tokens": tracker.get_usage_stats(),
        "database": get_stats()
    }

# ── Autocomplete endpoints ──────────────────────────────────
@router.get("/autocomplete/locations")
def autocomplete_locations(q: Optional[str] = Query("", description="Partial location name")):
    """Return distinct locations matching a partial query."""
    return {"results": get_unique_locations(q)}

@router.get("/autocomplete/cuisines")
def autocomplete_cuisines(q: Optional[str] = Query("", description="Partial cuisine name")):
    """Return distinct cuisines matching a partial query."""
    return {"results": get_unique_cuisines(q)}

@router.post("/data/refresh")
def refresh_data(background_tasks: BackgroundTasks):
    """Trigger an async refresh of data from HuggingFace to SQLite."""
    def _refreshTask():
        try:
            logger.info("Starting data refresh task...")
            # get_processed_restaurants(force_refresh=True) will download and clean
            # We don't have force_refresh implemented in phase2 ingestion_service perfectly, 
            # so we'll just get current and upsert to DB.
            df = get_processed_restaurants()
            upsert_restaurants(df)
            logger.info(f"Data refresh complete. Upserted {len(df)} records to SQLite.")
        except Exception as e:
            logger.error(f"Data refresh failed: {str(e)}", extra={"extra_info": {"error_type": type(e).__name__}})

    background_tasks.add_task(_refreshTask)
    return {"status": "accepted", "message": "Data refresh started in background."}

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """
    Production recommendation endpoint.
    Uses async LLM calls, token budgets, and structured logging.
    """
    start_time = time.perf_counter()
    req_id = f"req_{uuid.uuid4().hex[:8]}"
    
    try:
        # Pull directly from Phase 3 SQLite Database
        restaurants_df = get_all_restaurants()
        
        filtered = filter_restaurants(restaurants_df, request)
        if filtered.empty:
            logger.info("No candidates found.", extra={"extra_info": {"request_id": req_id, "duration_ms": 0}})
            return RecommendationResponse(
                total_candidates=0,
                returned_recommendations=0,
                recommendations=[]
            )

        ranked = rank_filtered_restaurants(filtered, request, top_k=20)
        
        # Phase 3 feature: ASYNC LLM CALL
        recommendations = await generate_recommendations_with_llm_async(request, ranked)
        
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        logger.info(
            "Recommendation served successfully.", 
            extra={"extra_info": {
                "request_id": req_id, 
                "total_candidates": len(ranked),
                "returned": len(recommendations),
                "duration_ms": duration_ms
            }}
        )
        
        return RecommendationResponse(
            total_candidates=len(ranked),
            returned_recommendations=len(recommendations),
            recommendations=recommendations
        )
        
    except Exception as exc:
        logger.error(
            "Recommendation request failed.", 
            extra={"extra_info": {"request_id": req_id, "error": str(exc)}}
        )
        raise HTTPException(status_code=500, detail="Internal server error executing recommendation logic.")
