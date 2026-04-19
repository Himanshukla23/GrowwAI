import asyncio
import json
import logging
from typing import List
import pandas as pd

from src.phase2.app.schemas import RecommendationRequest, RecommendationItem
# We reuse Phase 2's builder/parser/fallback functions directly
from src.phase2.app.services.llm_service import (
    _make_cache_key,
    _read_cache,
    _write_cache,
    _prompt,
    _safe_parse_llm_json,
    _fallback_top5
)
from src.phase2.app.config import settings as p2_settings
from ..config import settings as p3_settings
from .token_tracker import tracker

logger = logging.getLogger("phase3.async_llm")

# Because Groq is a sync client in Phase2's implementation, 
# we need an async client for true Phase3 performance
from groq import AsyncGroq

# Global async client initialized lazily
_async_client = None

def _get_async_client() -> AsyncGroq:
    global _async_client
    if _async_client is None:
        _async_client = AsyncGroq(api_key=p2_settings.GROQ_API_KEY)
    return _async_client

async def generate_recommendations_with_llm_async(
    request: RecommendationRequest,
    ranked_candidates_df: pd.DataFrame,
) -> List[RecommendationItem]:
    """
    Robust Phase 3 asynchronous wrapper for the LLM call.
    Includes: Retries, Timeouts, Event-Loop Non-Blocking execution, Token Budget limits.
    """
    if ranked_candidates_df.empty:
        return []

    llm_input_df = ranked_candidates_df.head(20).copy()
    llm_input = llm_input_df[
        ["name", "location", "cuisine", "rating", "avg_cost", "cost"]
    ].to_dict(orient="records")
    
    # Cast numpy types to native python types to prevent json serialization errors
    for row in llm_input:
        row["rating"] = float(row["rating"]) if pd.notnull(row["rating"]) else 0.0
        row["avg_cost"] = int(row["avg_cost"]) if pd.notnull(row["avg_cost"]) else 0

    cache_key = _make_cache_key(request, llm_input)
    
    # 1. Check cache (Sync operation, perfectly fast enough)
    cached = _read_cache(cache_key)
    if cached is not None:
        logger.info(f"LLM cache hit for cache_key starting with... {cache_key[:30]}")
        return cached

    # 2. Key Check
    if not p2_settings.GROQ_API_KEY:
        logger.warning("No GROQ_API_KEY. Using fallback.")
        fallback = _fallback_top5(llm_input_df)
        _write_cache(cache_key, fallback)
        return fallback

    # 3. Budget Check (Estimate 500 prompt + 500 output tokens)
    estimated_tokens = 1000 
    if not tracker.check_budget(estimated_tokens):
        logger.error(f"Token budget exhausted. Daily usage: {tracker._daily_usage}")
        fallback = _fallback_top5(llm_input_df)
        _write_cache(cache_key, fallback)
        return fallback

    prompt_text = _prompt(request, json.dumps(llm_input, ensure_ascii=True))
    client = _get_async_client()
    
    # 4. Async Execution with Timeout and Retries
    for attempt in range(1, p3_settings.LLM_MAX_RETRIES + 1):
        try:
            logger.info(f"LLM async API call (Attempt {attempt}/{p3_settings.LLM_MAX_RETRIES})...")
            
            # Run the call with asyncio timeout
            async with asyncio.timeout(p3_settings.LLM_TIMEOUT_SECONDS):
                response = await client.chat.completions.create(
                    model=p2_settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a food recommendation expert."},
                        {"role": "user", "content": prompt_text},
                    ],
                    temperature=0.2,
                )
                
            content = (response.choices[0].message.content or "").strip()
            
            # Record Token Usage
            if response.usage:
                tracker.record_usage(response.usage.total_tokens)
            
            # Parse logic
            parsed = _safe_parse_llm_json(content)

            recommendations: List[RecommendationItem] = []
            for row in parsed[:5]:
                recommendations.append(
                    RecommendationItem(
                        name=str(row.get("name", "")),
                        location=str(row.get("location", "")),
                        cuisine=str(row.get("cuisine", "")),
                        rating=float(row.get("rating", 0.0)),
                        avg_cost=int(row.get("avg_cost", 0)),
                        cost=str(row.get("cost", "")),
                        reason=str(row.get("reason", "")).strip() or "Good match for your preferences.",
                    )
                )

            if not recommendations or all(not item.name for item in recommendations):
                raise ValueError("Parsed JSON resulted in empty/invalid list.")

            _write_cache(cache_key, recommendations)
            return recommendations
            
        except TimeoutError:
            logger.error(f"LLM request timed out after {p3_settings.LLM_TIMEOUT_SECONDS}s.")
        except Exception as e:
            logger.error(f"LLM API request failed: {str(e)}")
            
        # Wait before retry (exponential backoff: 1s, then 2s)
        if attempt < p3_settings.LLM_MAX_RETRIES:
            await asyncio.sleep(2 ** (attempt - 1))

    # All attempts failed -> fallback
    logger.critical("All LLM attempts failed. Engaging fallback.")
    fallback = _fallback_top5(llm_input_df)
    _write_cache(cache_key, fallback)
    return fallback
