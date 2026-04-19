from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phase2.app.config import settings


def _safe_print(text: str) -> None:
    # Avoid Windows console encoding crashes on symbols like INR (₹).
    try:
        print(text)
    except UnicodeEncodeError:
        sanitized = text.encode("ascii", "replace").decode("ascii")
        print(sanitized)


@dataclass
class TestCase:
    name: str
    prompt: str


def _build_client() -> Groq:
    load_dotenv()
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing in .env file.")
    return Groq(api_key=settings.GROQ_API_KEY)


def _run_test(client: Groq, test: TestCase) -> dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful food recommendation assistant."},
                {"role": "user", "content": test.prompt},
            ],
            temperature=0.2,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return {
                "status": "FAIL",
                "error": "Empty response from model.",
                "response": "",
            }
        return {"status": "PASS", "error": "", "response": text}
    except Exception as exc:
        return {"status": "FAIL", "error": str(exc), "response": ""}


def main() -> None:
    tests = [
        TestCase(
            name="1) Basic prompt",
            prompt="Suggest 3 restaurants in Delhi. Keep it short.",
        ),
        TestCase(
            name="2) Structured user preferences",
            prompt=(
                "You are a food recommendation assistant.\n"
                "User Preferences:\n"
                "- Location: Delhi\n"
                "- Budget: medium\n"
                "- Cuisine: north indian\n"
                "- Minimum Rating: 4.0\n"
                "- Extra Preferences: family friendly\n"
                "Return 3 concise recommendations."
            ),
        ),
        TestCase(
            name="3) Edge case minimal input",
            prompt="Restaurant suggestions?",
        ),
        TestCase(
            name="4) Multi-preference query",
            prompt=(
                "Recommend 5 options in Delhi for a date night with vegetarian choices, "
                "quiet ambience, under medium budget, and rating above 4 if possible."
            ),
        ),
    ]

    print("=== LLM Integration Test Runner ===")
    print(f"Model: {settings.GROQ_MODEL}")
    print("API key source: .env via environment variables")
    print("-----------------------------------")

    try:
        client = _build_client()
    except Exception as exc:
        print("Initialization: FAIL")
        print(f"Error: {exc}")
        print("\nPer-test results:")
        for test in tests:
            print(f"\n{test.name}")
            print("Status: FAIL")
            print(f"Error: {exc}")
        print("\n=== Summary ===")
        print(json.dumps({"passed": 0, "failed": len(tests), "total": len(tests)}, indent=2))
        return

    results: list[tuple[str, dict[str, Any]]] = []
    for test in tests:
        result = _run_test(client, test)
        results.append((test.name, result))

    for name, result in results:
        print(f"\n{name}")
        print(f"Status: {result['status']}")
        if result["status"] == "PASS":
            print("Response:")
            _safe_print(result["response"])
        else:
            print(f"Error: {result['error']}")

    passed = sum(1 for _, r in results if r["status"] == "PASS")
    failed = len(results) - passed
    print("\n=== Summary ===")
    print(json.dumps({"passed": passed, "failed": failed, "total": len(results)}, indent=2))


if __name__ == "__main__":
    main()
