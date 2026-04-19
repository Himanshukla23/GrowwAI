from __future__ import annotations

import pandas as pd

from ..schemas import RecommendationRequest
from .semantic_service import SemanticSearchService

semantic_search = SemanticSearchService()


def _contains(series: pd.Series, value: str) -> pd.Series:
    return series.astype(str).str.contains(value, case=False, na=False)


def _cost_match_score(cost_series: pd.Series, budget: str) -> pd.Series:
    return (cost_series == budget).astype(float)


def _relevance_query(request: RecommendationRequest) -> str:
    return " ".join(
        item for item in [request.location, request.cuisine, request.extra_preferences] if item
    ).strip()


def filter_restaurants(df: pd.DataFrame, request: RecommendationRequest) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    
    # Location filtering - Case insensitive inclusion
    # If DB has 'indiranagar' and user searches 'Indiranagar, Bangalore', it should match
    # So we check if the user query contains the DB location OR the DB location contains the user query
    if request.location:
        query = request.location.lower().strip()
        filtered = filtered[
            filtered["location"].str.lower().apply(lambda x: x in query or query in x)
        ]
    
    # Cuisine filtering - Support multiple cuisines (ANY match)
    if request.cuisine:
        cuisine_list = [c.strip().lower() for c in request.cuisine.split(",")]
        # Create a combined mask for all cuisines
        cuisine_mask = pd.Series(False, index=filtered.index)
        for cuisine in cuisine_list:
            if cuisine:
                # Same logic for cuisines to be robust
                cuisine_mask |= filtered["cuisine"].str.lower().str.contains(cuisine, case=False, na=False)
        filtered = filtered[cuisine_mask]
    
    # Rating filtering - with fallback for low result density
    r_val = float(request.min_rating or 4.0)
    mask = filtered["rating"] >= r_val
    if mask.sum() < 5:
        # Loosen by 0.5 if too restrictive, but stay above 3.0
        r_val = max(3.0, r_val - 0.5)
        mask = filtered["rating"] >= r_val
    filtered = filtered[mask]
    
    # Budget filtering
    if request.budget:
        filtered = filtered[filtered["cost"] == request.budget]
        
    return filtered.reset_index(drop=True)


def rank_filtered_restaurants(
    filtered_df: pd.DataFrame,
    request: RecommendationRequest,
    top_k: int = 20,
) -> pd.DataFrame:
    if filtered_df.empty:
        return filtered_df

    ranked = filtered_df.copy()
    ranked["rating_score"] = ranked["rating"] / 5.0
    ranked["cost_score"] = _cost_match_score(ranked["cost"], request.budget)
    ranked["semantic_score"] = semantic_search.score(_relevance_query(request), ranked)

    ranked["final_score"] = (
        0.60 * ranked["rating_score"]
        + 0.20 * ranked["cost_score"]
        + 0.20 * ranked["semantic_score"]
    )
    ranked = ranked.sort_values(
        by=["final_score", "rating", "semantic_score"],
        ascending=False,
    )
    return ranked.head(top_k).reset_index(drop=True)
