"""
Phase 9: API and Multi-Thread Chat Layer

Adheres to rag-architecture.md Section 4.7:
- POST /chat/{thread_id}/query   — Ask a factual question within a thread
- POST /threads                  — Create a new conversation thread
- GET  /threads/{thread_id}/history — Retrieve conversation history
- GET  /health                   — Service health check

Thread model:
- Independent thread context with minimal memory.
- Context carries: selected AMC/scheme hints, prior factual entities,
  latest successful citation context.
- Retrieval remains mandatory for every response (no pure-memory answers).
"""
import os
import sys
import uuid
import pathlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ── Project root & env ────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

# ── Sibling phase imports ─────────────────────────────────────────────────────
sys.path.insert(0, str(ROOT / "backend" / "phase-6-retrieval-reranking-layer" / "src"))
sys.path.insert(0, str(ROOT / "backend" / "phase-7-grounded-answer-generation" / "src"))
sys.path.insert(0, str(ROOT / "backend" / "phase-8-policy-safety-guardrails" / "src"))
sys.path.insert(0, str(ROOT / "backend" / "phase-10-observability-evaluation" / "src"))

from retriever import Retriever
from pipeline import RetrievalPipeline
from generator import AnswerGenerator
from guardrails import PolicyGuardrails
from observability import ObservabilityStore, RequestLog

# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title="Groww Assist — Advanced Mutual Fund Analyst",
    description="Premium RAG-powered financial intelligence assistant for Groww users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ──────────────────────────────────────────────────────────

class ThreadCreate(BaseModel):
    """Request body to create a new thread (optional context hints)."""
    amc_hint: Optional[str] = None
    scheme_hint: Optional[str] = None


class ThreadResponse(BaseModel):
    thread_id: str
    created_at: str
    context: Dict


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class QueryResponse(BaseModel):
    thread_id: str
    query: str
    answer: str
    intent: str
    rewritten_query: Optional[str] = None
    chunks_used: int = 0
    guardrail_violations: List[str] = []
    structured_data: Optional[Dict] = None
    citation_url: Optional[str] = None
    timestamp: str


class HistoryMessage(BaseModel):
    role: str            # "user" | "assistant"
    content: str
    timestamp: str
    intent: Optional[str] = None


class HistoryResponse(BaseModel):
    thread_id: str
    messages: List[HistoryMessage]


class HealthResponse(BaseModel):
    status: str
    version: str
    chroma_collection: str
    indexed_chunks: int
    timestamp: str


# ── In-memory thread store (§4.7 minimal memory) ─────────────────────────────
# Production upgrade: replace with a relational DB (Postgres, SQLite, etc.)

_threads: Dict[str, Dict] = {}


def _get_thread(thread_id: str) -> Dict:
    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found.")
    return _threads[thread_id]


# ── Lazy-init singletons ─────────────────────────────────────────────────────
_retriever: Optional[Retriever] = None
_pipeline: Optional[RetrievalPipeline] = None
_generator: Optional[AnswerGenerator] = None
_guardrails: Optional[PolicyGuardrails] = None
_observability: Optional[ObservabilityStore] = None


def _init_components():
    global _retriever, _pipeline, _generator, _guardrails, _observability
    if _retriever is None:
        print("[API] Initializing RAG components…")
        _retriever = Retriever()
        _pipeline = RetrievalPipeline(_retriever)
        _generator = AnswerGenerator()
        _guardrails = PolicyGuardrails()
        _observability = ObservabilityStore()
        print("[API] All components ready.")


@app.on_event("startup")
async def startup():
    _init_components()


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    """Service health check."""
    _init_components()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        chroma_collection=_retriever.collection.name,
        indexed_chunks=_retriever.collection.count(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/threads", response_model=ThreadResponse)
async def create_thread(body: ThreadCreate = None):
    """Create a new conversation thread."""
    body = body or ThreadCreate()
    thread_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    _threads[thread_id] = {
        "created_at": now,
        "context": {
            "amc_hint": body.amc_hint,
            "scheme_hint": body.scheme_hint,
            "prior_entities": [],
            "latest_citation": None,
        },
        "messages": [],
    }

    return ThreadResponse(
        thread_id=thread_id,
        created_at=now,
        context=_threads[thread_id]["context"],
    )


@app.get("/threads/{thread_id}/history", response_model=HistoryResponse)
async def get_history(thread_id: str):
    """Return the full conversation history for a thread."""
    thread = _get_thread(thread_id)
    return HistoryResponse(thread_id=thread_id, messages=thread["messages"])


@app.post("/chat/{thread_id}/query", response_model=QueryResponse)
async def chat_query(thread_id: str, body: QueryRequest):
    """
    Accept a user question, run the full RAG pipeline, and return a
    grounded answer.  Every response is freshly retrieved — thread context
    only provides optional metadata hints.
    """
    import time as _time
    _init_components()
    thread = _get_thread(thread_id)
    now = datetime.now(timezone.utc).isoformat()
    query = body.query.strip()
    req_log = RequestLog()

    # ── 1. Pre-generation guardrails ──────────────────────────────────────
    t0 = _time.time()
    pre_result = _guardrails.pre_generate(query)
    req_log.set_latency("guardrail", (_time.time() - t0) * 1000)
    req_log.set_guardrail_pre(pre_result["allowed"])

    if not pre_result["allowed"]:
        refusal = pre_result["refusal_message"]
        req_log.set_query(query, pre_result["block_reason"])
        _observability.record(req_log)
        # Record in thread history
        thread["messages"].append(HistoryMessage(role="user", content=query, timestamp=now))
        thread["messages"].append(
            HistoryMessage(role="assistant", content=refusal, timestamp=now, intent=pre_result["block_reason"])
        )
        return QueryResponse(
            thread_id=thread_id,
            query=query,
            answer=refusal,
            intent=pre_result["block_reason"],
            chunks_used=0,
            timestamp=now,
        )

    # ── 2. Build metadata filters from thread context ─────────────────────
    ctx = thread["context"]
    filters = {}
    if ctx.get("amc_hint"):
        filters["amc_name"] = ctx["amc_hint"]

    # ── 3. Retrieval & re-ranking pipeline ────────────────────────────────
    t1 = _time.time()
    pipeline_result = _pipeline.run(query=query, filters=filters or None)
    req_log.set_latency("retrieve", (_time.time() - t1) * 1000)

    if pipeline_result.get("error"):
        # Pipeline-level guardrail (advisory / out-of-scope from LLM intent)
        refusal = pipeline_result["error"]
        intent = pipeline_result.get("intent", "blocked")
        req_log.set_query(query, intent)
        _observability.record(req_log)
        thread["messages"].append(HistoryMessage(role="user", content=query, timestamp=now))
        thread["messages"].append(
            HistoryMessage(role="assistant", content=refusal, timestamp=now, intent=intent)
        )
        return QueryResponse(
            thread_id=thread_id,
            query=query,
            answer=refusal,
            intent=intent,
            chunks_used=0,
            timestamp=now,
        )

    req_log.set_query(query, pipeline_result.get("intent", "factual"))
    req_log.set_rewritten_query(pipeline_result.get("rewritten_query", query))
    all_chunk_ids = [c["chunk_id"] for c in pipeline_result.get("raw_results", [])]
    selected_ids = all_chunk_ids[:3]
    req_log.set_retrieval(all_chunk_ids, selected_ids)

    # ── 4. Generate grounded answer ───────────────────────────────────────
    evidence_context = pipeline_result.get("evidence_context", "")
    print(f"\n[DEBUG] Chunks Packed: {pipeline_result.get('chunks_used')}")
    print(f"[DEBUG] Evidence Length: {len(evidence_context)}")
    t2 = _time.time()
    raw_answer = _generator.generate_answer(query, evidence_context)
    req_log.set_latency("generate", (_time.time() - t2) * 1000)

    # ── 5. Post-generation guardrails ─────────────────────────────────────
    post_result = _guardrails.post_generate(raw_answer)
    final_answer = post_result["corrected_answer"]
    violations = post_result["violations"]
    req_log.set_guardrail_post(post_result["compliant"], violations)
    req_log.set_answer_length(len(final_answer))

    # Extract citation URL from top chunk for UI buttons & logging
    top_chunks = pipeline_result.get("raw_results", [])
    citation_url = top_chunks[0].get("metadata", {}).get("source_url") if top_chunks else None
    ctx["latest_citation"] = citation_url
    req_log.set_citation(citation_url)
    # Extract scheme names mentioned to help future queries
    for chunk in pipeline_result.get("raw_results", []):
        scheme = chunk.get("metadata", {}).get("scheme_name")
        if scheme and scheme not in ctx["prior_entities"]:
            ctx["prior_entities"].append(scheme)

    # (Information already extracted above from metadata)

    # ── 8. Persist observability log ──────────────────────────────────────
    _observability.record(req_log)

    # ── 9. Record in thread history ───────────────────────────────────────
    thread["messages"].append(HistoryMessage(role="user", content=query, timestamp=now))
    thread["messages"].append(
        HistoryMessage(
            role="assistant",
            content=final_answer,
            timestamp=now,
            intent=pipeline_result.get("intent"),
        )
    )

    # ── 10. Extract structured data for frontend UI ───────────────────────
    structured_data = None
    if pipeline_result.get("intent") in ["factual", "comparison"]:
        structured_data = _generator.extract_fund_data(
            evidence_context, 
            intent=pipeline_result.get("intent")
        )

    return QueryResponse(
        thread_id=thread_id,
        query=query,
        answer=final_answer,
        intent=pipeline_result.get("intent", "factual"),
        rewritten_query=pipeline_result.get("rewritten_query"),
        chunks_used=pipeline_result.get("chunks_used", 0),
        guardrail_violations=violations,
        structured_data=structured_data,
        citation_url=ctx.get("latest_citation"),
        timestamp=now,
    )


@app.get("/metrics")
async def metrics():
    """Return aggregate observability dashboard metrics (§4.9)."""
    _init_components()
    return _observability.get_metrics()


# ── Environment ───────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


# ── Run with: python app.py ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # Render provides a PORT environment variable
    port = int(os.getenv("PORT", 8000))
    print(f"[API] Starting server on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
