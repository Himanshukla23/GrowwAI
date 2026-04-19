from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phase2.app.main import app
from src.phase2.app.schemas import RecommendationItem
from src.phase4.backend import services as phase4_services_pkg  # noqa: F401
from src.phase4.backend.services import orchestrator


def _mock_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "Spice Garden",
                "location": "delhi",
                "cuisine": "north indian",
                "avg_cost": 800,
                "rating": 4.3,
                "cost": "medium",
            },
            {
                "name": "Green Bowl",
                "location": "delhi",
                "cuisine": "north indian",
                "avg_cost": 700,
                "rating": 4.1,
                "cost": "medium",
            },
        ]
    )


def _apply_mocks() -> None:
    orchestrator.get_processed_restaurants = lambda: _mock_df()
    orchestrator.filter_restaurants = lambda df, request: df.copy()
    orchestrator.rank_filtered_restaurants = lambda df, request, top_k=20: df.head(top_k).copy()
    orchestrator.generate_recommendations_with_llm = (
        lambda request, ranked_df: [
            RecommendationItem(
                name=str(row["name"]),
                location=str(row["location"]),
                cuisine=str(row["cuisine"]),
                rating=float(row["rating"]),
                avg_cost=int(row["avg_cost"]),
                cost=str(row["cost"]),
                reason="Mocked LLM response",
            )
            for _, row in ranked_df.head(2).iterrows()
        ]
    )


def _print_result(name: str, status: bool, response_json: dict) -> None:
    print(f"\n{name}")
    print(f"Status: {'PASS' if status else 'FAIL'}")
    print("Response:")
    print(json.dumps(response_json, indent=2))


def main() -> None:
    _apply_mocks()
    client = TestClient(app)

    base_payload = {
        "location": "delhi",
        "budget": "medium",
        "cuisine": "north indian",
        "min_rating": 4.0,
        "extra_preferences": "family",
    }

    # Test 1: Single recommend endpoint.
    resp1 = client.post("/phase4/recommend", json=base_payload)
    ok1 = resp1.status_code == 200 and resp1.json().get("returned_recommendations", 0) > 0
    _print_result("1) /phase4/recommend", ok1, resp1.json())

    # Test 2: Explain endpoint.
    resp2 = client.post("/phase4/recommend/explain", json=base_payload)
    j2 = resp2.json()
    ok2 = (
        resp2.status_code == 200
        and "filtering_summary" in j2
        and j2.get("llm_summary", {}).get("filter_before_llm_enforced") is True
    )
    _print_result("2) /phase4/recommend/explain", ok2, j2)

    # Test 3: Batch endpoint with two requests.
    resp3 = client.post("/phase4/recommend/batch", json={"requests": [base_payload, base_payload]})
    j3 = resp3.json()
    ok3 = resp3.status_code == 200 and j3.get("batch_size") == 2 and len(j3.get("results", [])) == 2
    _print_result("3) /phase4/recommend/batch", ok3, j3)

    passed = sum([ok1, ok2, ok3])
    failed = 3 - passed
    print("\n=== Summary ===")
    print(json.dumps({"passed": passed, "failed": failed, "total": 3}, indent=2))


if __name__ == "__main__":
    main()
