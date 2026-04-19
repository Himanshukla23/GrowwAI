# Groww Assist — Backend Architecture

This directory organizes the project by architecture phases defined in `docs/rag-architecture.md` (Section 3: High-Level System Architecture).

- `phase-1-scheduler-service`: GitHub Actions cron + orchestration.
- `phase-2-scraping-service`: Groww URL fetch and text cleaning.
- `phase-3-source-intake-layer`: Source registry and domain allowlist control.
- `phase-4-document-processing-normalization`: Text chunking and metadata enrichment.
- `phase-5-indexing-layer`: ChromaDB vector indexing with `bge-base-en-v1.5` embeddings.
- `phase-6-retrieval-reranking-layer`: Hybrid semantic search, metadata filtering, and heuristic re-ranking.
- `phase-7-grounded-answer-generation`: Groq LLM generation with strict grounding constraints.
- `phase-8-policy-safety-guardrails`: Intent classification, PII detection, and safety checks.
- `phase-9-api-multi-thread-chat`: FastAPI endpoints with multi-thread conversation support.
- `phase-10-observability-evaluation`: JSONL structured logging, per-request metrics, and dashboard aggregation.

## Implementation Status

| Phase | Component | Status |
|---|---|---|
| Phase 1 | Scheduler Service | ✅ Complete |
| Phase 2 | Scraping Service | ✅ Complete |
| Phase 3 | Source Intake Layer | ✅ Complete |
| Phase 4 | Document Processing | ✅ Complete |
| Phase 5 | Indexing Layer (ChromaDB) | ✅ Complete |
| Phase 6 | Retrieval & Re-ranking | ✅ Complete |
| Phase 7 | Grounded Answer Generation | ✅ Complete |
| Phase 8 | Policy & Safety Guardrails | ✅ Complete |
| Phase 9 | API & Multi-Thread Chat | ✅ Complete |
| Phase 10 | Observability & Evaluation | ✅ Complete |

## Running the Backend

```bash
# From the project root
pip install -r requirements.txt

# Start the API server
cd backend/phase-9-api-multi-thread-chat/src
uvicorn app:app --reload --port 8000
```

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/threads` | Create a new conversation thread |
| `GET` | `/threads/{thread_id}/history` | Get thread conversation history |
| `POST` | `/chat/{thread_id}/query` | Submit a query to the RAG pipeline |
| `GET` | `/metrics` | Aggregate observability metrics |
