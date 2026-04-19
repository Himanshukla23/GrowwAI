from __future__ import annotations

from ..app.schemas import RecommendationRequest
from ..app.services.filter_service import filter_restaurants, rank_filtered_restaurants
from ..app.services.ingestion_service import get_processed_restaurants
from ..app.services.llm_service import generate_recommendations_with_llm


def _ask(prompt: str) -> str:
    return input(prompt).strip()


def _collect_input() -> RecommendationRequest:
    location = _ask("Location: ").lower()
    budget = _ask("Budget (low/medium/high): ").lower()
    cuisine = _ask("Cuisine: ").lower()
    min_rating_raw = _ask("Minimum rating (0-5): ")
    extra_preferences = _ask("Extra preferences (optional, e.g. date/family/quick bite): ")

    min_rating = float(min_rating_raw) if min_rating_raw else 0.0
    return RecommendationRequest(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        extra_preferences=extra_preferences,
    )


def _print_results(total_candidates: int, recommendations: list) -> None:
    print("\n" + "=" * 72)
    print(f"Shortlisted candidates for LLM: {total_candidates}")
    print(f"Final recommendations: {len(recommendations)}")
    print("=" * 72)

    if not recommendations:
        print("No restaurants matched your filters. Try broadening inputs.")
        return

    for idx, item in enumerate(recommendations, start=1):
        print(f"\n{idx}. {item.name}")
        print(f"   Location: {item.location}")
        print(f"   Cuisine : {item.cuisine}")
        print(f"   Rating  : {item.rating}")
        print(f"   Cost    : {item.cost} (avg_cost={item.avg_cost})")
        print(f"   Why     : {item.reason}")


def main() -> None:
    print("Restaurant Recommendation CLI (Phase 2)")
    try:
        request = _collect_input()
        restaurants_df = get_processed_restaurants()
        filtered = filter_restaurants(restaurants_df, request)
        ranked = rank_filtered_restaurants(filtered, request, top_k=20)
        recommendations = generate_recommendations_with_llm(request, ranked)
        _print_results(len(ranked), recommendations)
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
