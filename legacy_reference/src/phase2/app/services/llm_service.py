from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Tuple

import pandas as pd
from groq import Groq

from ..config import settings
from ..schemas import RecommendationItem, RecommendationRequest

_llm_cache: Dict[str, Tuple[float, List[RecommendationItem]]] = {}


def _make_cache_key(request: RecommendationRequest, candidates: List[Dict[str, Any]]) -> str:
    payload = {
        "request": request.model_dump(),
        "candidates": candidates,
        "model": settings.GROQ_MODEL,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True)


def _read_cache(key: str) -> List[RecommendationItem] | None:
    cached = _llm_cache.get(key)
    if not cached:
        return None
    expires_at, value = cached
    if time.time() > expires_at:
        _llm_cache.pop(key, None)
        return None
    return value


def _write_cache(key: str, recommendations: List[RecommendationItem]) -> None:
    if len(_llm_cache) >= settings.LLM_CACHE_MAX_ITEMS:
        oldest_key = next(iter(_llm_cache.keys()))
        _llm_cache.pop(oldest_key, None)
    _llm_cache[key] = (time.time() + settings.LLM_CACHE_TTL_SECONDS, recommendations)


def _prompt(request: RecommendationRequest, filtered_json: str) -> str:
    return f"""
You are a food recommendation expert.

User Preferences:
- Location: {request.location}
- Budget: {request.budget}
- Cuisine: {request.cuisine}
- Minimum Rating: {request.min_rating}
- Extra Preferences: {request.extra_preferences or "none"}

Interpret extra preferences naturally.
Examples:
- "date" => romantic/quiet vibe
- "family" => kid-friendly and spacious
- "quick bite" => fast service and simple options

Restaurants (already filtered shortlist, never full dataset):
{filtered_json}

Tasks:
1) Choose and rank the top 5.
2) Keep reason short, personalized, and practical.
3) Do not invent restaurants not listed in input.
4) Output strict JSON array only.

Output JSON format:
[
  {{
    "name": "",
    "location": "",
    "cuisine": "",
    "rating": 0.0,
    "avg_cost": 0,
    "cost": "",
    "reason": ""
  }}
]
""".strip()


def _safe_parse_llm_json(raw_text: str) -> list[dict[str, Any]]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError("LLM output is not a list.")
    return parsed


def _fallback_top5(candidates_df: pd.DataFrame) -> List[RecommendationItem]:
    top = candidates_df.head(5).to_dict(orient="records")
    output: List[RecommendationItem] = []
    for row in top:
        output.append(
            RecommendationItem(
                name=str(row["name"]),
                location=str(row["location"]),
                cuisine=str(row["cuisine"]),
                rating=float(row["rating"]),
                avg_cost=int(row["avg_cost"]),
                cost=str(row["cost"]),
                reason="Strong match based on your filters and ranking score.",
            )
        )
    return output


def generate_recommendations_with_llm(
    request: RecommendationRequest,
    ranked_candidates_df: pd.DataFrame,
) -> List[RecommendationItem]:
    if ranked_candidates_df.empty:
        return []

    llm_input_df = ranked_candidates_df.head(20).copy()
    llm_input = llm_input_df[
        ["name", "location", "cuisine", "rating", "avg_cost", "cost"]
    ].to_dict(orient="records")

    cache_key = _make_cache_key(request, llm_input)
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    if not settings.GROQ_API_KEY:
        fallback = _fallback_top5(llm_input_df)
        _write_cache(cache_key, fallback)
        return fallback

    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = _prompt(request, json.dumps(llm_input, ensure_ascii=True))

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a food recommendation expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = (response.choices[0].message.content or "").strip()
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
                    reason=str(row.get("reason", "")).strip()
                    or "Good match for your preferences.",
                )
            )

        if not recommendations or all(not item.name for item in recommendations):
            recommendations = _fallback_top5(llm_input_df)

        _write_cache(cache_key, recommendations)
        return recommendations
    except Exception:
        fallback = _fallback_top5(llm_input_df)
        _write_cache(cache_key, fallback)
        return fallback
