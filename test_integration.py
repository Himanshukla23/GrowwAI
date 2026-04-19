"""
GrowwAI / Groww Assist - Integration Test Suite
Tests backend API endpoints and frontend-backend connectivity.
"""
import requests
import json
import time
import sys
import os

# Force UTF-8 output on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_URL = "http://localhost:8000"

PASS_COUNT = 0
FAIL_COUNT = 0
RESULTS = []

def test(name, condition, details=""):
    global PASS_COUNT, FAIL_COUNT
    status = "PASS" if condition else "FAIL"
    icon = "+" if condition else "x"
    if condition:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    RESULTS.append({"name": name, "status": status, "details": details})
    safe_details = details.replace('\u20b9', 'Rs.') if details else ""
    print(f"  [{icon}] {name}")
    if safe_details:
        safe_out = safe_details[:200].encode('ascii', errors='replace').decode('ascii')
        print(f"       {safe_out}")

print("=" * 70)
print("GROWW ASSIST -- INTEGRATION TEST SUITE")
print("=" * 70)

# TEST 1: Health Check
print("\n-- Test 1: Health Check --")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    data = r.json()
    test("Health endpoint returns 200", r.status_code == 200)
    test("Status is 'healthy'", data.get("status") == "healthy", f"Got: {data.get('status')}")
    test("Collection name present", bool(data.get("chroma_collection")), f"Collection: {data.get('chroma_collection')}")
    test("Indexed chunks > 0", data.get("indexed_chunks", 0) > 0, f"Chunks: {data.get('indexed_chunks')}")
    test("Version is 1.0.0", data.get("version") == "1.0.0")
except Exception as e:
    test("Health endpoint reachable", False, str(e))

# TEST 2: Thread Creation
print("\n-- Test 2: Thread Creation --")
thread_id = None
try:
    r = requests.post(f"{BASE_URL}/threads", timeout=10)
    data = r.json()
    thread_id = data.get("thread_id")
    test("Thread creation returns 200", r.status_code == 200)
    test("Thread ID is UUID format", thread_id is not None and len(thread_id) == 36, f"ID: {thread_id}")
    test("Context has expected keys", "amc_hint" in data.get("context", {}))
except Exception as e:
    test("Thread creation", False, str(e))

# TEST 3: Factual Query (RAG Pipeline End-to-End)
print("\n-- Test 3: Factual Query (E2E RAG) --")
if thread_id:
    try:
        r = requests.post(
            f"{BASE_URL}/chat/{thread_id}/query",
            json={"query": "What is the expense ratio of SBI Contra Fund?"},
            timeout=60
        )
        data = r.json()
        test("Query returns 200", r.status_code == 200)
        answer_preview = data.get("answer", "")[:150].encode('ascii', errors='replace').decode('ascii')
        test("Answer is non-empty", bool(data.get("answer")), f"Answer: {answer_preview}")
        test("Intent is 'factual'", data.get("intent") == "factual", f"Intent: {data.get('intent')}")
        test("Chunks used > 0", data.get("chunks_used", 0) > 0, f"Chunks: {data.get('chunks_used')}")
        test("Thread ID matches", data.get("thread_id") == thread_id)
        test("Timestamp present", bool(data.get("timestamp")))
        answer = data.get("answer", "").lower()
        test("Answer is not a corpus refusal", "cannot answer" not in answer, f"Got refusal: {answer[:100].encode('ascii', errors='replace').decode('ascii')}")
    except Exception as e:
        test("Factual query", False, str(e))
else:
    test("Factual query", False, "No thread_id available (thread creation failed)")

# TEST 4: Advisory Query (Should be blocked by guardrails)
print("\n-- Test 4: Advisory Query (Guardrail Block) --")
if thread_id:
    try:
        r = requests.post(
            f"{BASE_URL}/chat/{thread_id}/query",
            json={"query": "Should I invest in SBI Contra Fund?"},
            timeout=30
        )
        data = r.json()
        test("Advisory query returns 200", r.status_code == 200)
        test("Intent is 'advisory'", data.get("intent") == "advisory", f"Intent: {data.get('intent')}")
        answer = data.get("answer", "")
        test("Answer contains refusal", "cannot provide" in answer.lower() or "advice" in answer.lower() or "cannot" in answer.lower(), f"Answer: {answer[:150].encode('ascii', errors='replace').decode('ascii')}")
        test("Chunks used is 0", data.get("chunks_used", -1) == 0, f"Chunks: {data.get('chunks_used')}")
    except Exception as e:
        test("Advisory query", False, str(e))

# TEST 5: PII Detection (Should be blocked)
print("\n-- Test 5: PII Detection (Guardrail Block) --")
if thread_id:
    try:
        r = requests.post(
            f"{BASE_URL}/chat/{thread_id}/query",
            json={"query": "My PAN is ABCDE1234F, check my fund NAV"},
            timeout=30
        )
        data = r.json()
        test("PII query returns 200", r.status_code == 200)
        test("Intent is 'pii'", data.get("intent") == "pii", f"Intent: {data.get('intent')}")
        answer = data.get("answer", "")
        test("Answer contains PII warning", "personal information" in answer.lower() or "sensitive" in answer.lower(), f"Answer: {answer[:150].encode('ascii', errors='replace').decode('ascii')}")
    except Exception as e:
        test("PII detection", False, str(e))

# TEST 6: Thread History
print("\n-- Test 6: Thread History --")
if thread_id:
    try:
        r = requests.get(f"{BASE_URL}/threads/{thread_id}/history", timeout=10)
        data = r.json()
        test("History returns 200", r.status_code == 200)
        test("Thread ID matches", data.get("thread_id") == thread_id)
        msgs = data.get("messages", [])
        test("History has messages", len(msgs) > 0, f"Message count: {len(msgs)}")
        test("History has at least 6 messages (3 Q&A pairs)", len(msgs) >= 6, f"Count: {len(msgs)}")
    except Exception as e:
        test("Thread history", False, str(e))

# TEST 7: Invalid Thread ID
print("\n-- Test 7: Invalid Thread ID --")
try:
    r = requests.post(
        f"{BASE_URL}/chat/non-existent-thread/query",
        json={"query": "test"},
        timeout=10
    )
    test("Invalid thread returns 404", r.status_code == 404, f"Got: {r.status_code}")
except Exception as e:
    test("Invalid thread", False, str(e))

# TEST 8: Empty Query Validation
print("\n-- Test 8: Empty Query Validation --")
if thread_id:
    try:
        r = requests.post(
            f"{BASE_URL}/chat/{thread_id}/query",
            json={"query": ""},
            timeout=10
        )
        test("Empty query returns 422 (validation error)", r.status_code == 422, f"Got: {r.status_code}")
    except Exception as e:
        test("Empty query validation", False, str(e))

# TEST 9: Metrics Endpoint
print("\n-- Test 9: Observability Metrics --")
try:
    r = requests.get(f"{BASE_URL}/metrics", timeout=10)
    data = r.json()
    test("Metrics returns 200", r.status_code == 200)
    test("Total queries tracked", data.get("total_queries", 0) > 0, f"Total: {data.get('total_queries')}")
    test("Factual answer rate present", "factual_answer_rate" in data)
    test("Refusal rate present", "refusal_rate" in data)
    test("Query class breakdown present", bool(data.get("query_class_breakdown")))
except Exception as e:
    test("Metrics endpoint", False, str(e))

# TEST 10: CORS Headers (Frontend connectivity)
print("\n-- Test 10: CORS Headers --")
try:
    r = requests.options(
        f"{BASE_URL}/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        },
        timeout=10
    )
    cors_header = r.headers.get("access-control-allow-origin", "")
    test("CORS allows frontend origin", cors_header == "*" or "localhost:3000" in cors_header, f"CORS: {cors_header}")
except Exception as e:
    test("CORS headers", False, str(e))

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {PASS_COUNT} PASSED / {FAIL_COUNT} FAILED / {PASS_COUNT + FAIL_COUNT} TOTAL")
print("=" * 70)

if FAIL_COUNT > 0:
    print("\nFailed tests:")
    for r in RESULTS:
        if r["status"] == "FAIL":
            safe = r['details'].encode('ascii', errors='replace').decode('ascii') if r['details'] else ""
            print(f"  - {r['name']}: {safe}")

sys.exit(0 if FAIL_COUNT == 0 else 1)
