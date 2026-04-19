# Detailed RAG Architecture - Mutual Fund FAQ Assistant (Facts-Only)

## 1) Purpose and Design Principles

This architecture defines a Retrieval-Augmented Generation (RAG) system for answering objective mutual fund FAQs using a curated Groww mutual fund corpus (HTML pages only) for the current implementation scope.

Core principles:
- Facts-only answers; no advice, recommendation, or opinion.
- Every answer is grounded in retrieved source snippets.
- Short responses (max 3 sentences) with mandatory citation.
- Strict source allowlist and policy-first refusals.
- Transparent freshness metadata: `Last updated from sources: <date>`.

## 2) Scope Mapping from Problem Statement

- **Domain scope:** 4 AMCs and 15 curated Groww pages (4 AMC pages + 11 scheme pages).
- **Corpus source policy (current):** Groww web pages only.
- **PDF scope:** not included in current version.
- **Supported topics:** expense ratio, exit load, sector allocation, holdings, SIP minimum, ELSS lock-in, riskometer, benchmark, statement/tax process.
- **Unsupported topics:** recommendations, "which is better", return comparisons, investment advice.

## 2.1) Corpus Definition (In Scope URLs)

Source: `Groww`  
Description: Initial curated dataset of mutual fund schemes used for RAG retrieval.

### SBI Mutual Fund
- AMC page: `https://groww.in/mutual-funds/amc/sbi-mutual-funds`
- `SBI Gold Fund Direct Growth`: `https://groww.in/mutual-funds/sbi-gold-fund-direct-growth`
- `SBI PSU Fund Direct Growth`: `https://groww.in/mutual-funds/sbi-psu-fund-direct-growth`
- `SBI Small Midcap Fund Direct Growth`: `https://groww.in/mutual-funds/sbi-small-midcap-fund-direct-growth`
- `SBI Contra Fund Direct Growth`: `https://groww.in/mutual-funds/sbi-contra-fund-direct-growth`

### ICICI Prudential Mutual Fund
- AMC page: `https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds`
- `ICICI Prudential Dynamic Plan Direct Growth`: `https://groww.in/mutual-funds/icici-prudential-dynamic-plan-direct-growth`
- `ICICI Prudential Large Cap Fund Direct Growth`: `https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth`
- `ICICI Prudential Bharat 22 FOF Direct Growth`: `https://groww.in/mutual-funds/icici-prudential-bharat-22-fof-direct-growth`
- `ICICI Prudential Silver ETF FOF Direct Growth`: `https://groww.in/mutual-funds/icici-prudential-silver-etf-fof-direct-growth`

### HDFC Mutual Fund
- AMC page: `https://groww.in/mutual-funds/amc/hdfc-mutual-funds`
- `HDFC Mid Cap Fund Direct Growth`: `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth`
- `HDFC Equity Fund Direct Growth`: `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth`
- `HDFC Focused Fund Direct Growth`: `https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth`

### Nippon India Mutual Fund
- AMC page: `https://groww.in/mutual-funds/amc/nippon-india-mutual-funds`
- `Nippon India Growth Mid Cap Fund Direct Growth`: `https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth`
- `Nippon India Multi Cap Fund Direct Growth`: `https://groww.in/mutual-funds/nippon-india-multi-cap-fund-direct-growth`
- `Nippon India Multi Asset Omni FOF Direct Growth`: `https://groww.in/mutual-funds/nippon-india-multi-asset-omni-fof-direct-growth`
- `Nippon India Large Cap Fund Direct Growth`: `https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth`

Current constraints:
- Allowed sources: Groww web pages only.
- PDFs included: `false`.
- Note: No factsheets/SID/KIM PDFs in current scope. Future versions may ingest official AMC documents.

## 3) High-Level System Architecture

1. Scheduler Service  
2. Scraping Service  
3. Source Intake Layer  
4. Document Processing and Normalization Layer  
5. Indexing Layer (Vector + Metadata + Keyword)  
6. Retrieval and Re-ranking Layer  
7. Grounded Answer Generation Layer  
8. Policy and Safety Guardrail Layer  
9. API and Multi-thread Chat Layer  
10. Observability and Evaluation Layer

## 4) Component-Level Design

## 4.0 Scheduler Service

Responsibilities:
- Run a scheduled refresh job **daily at 09:15 IST**.
- Trigger the data ingestion pipeline for all configured corpus URLs.
- Ensure corpus freshness by initiating scrape -> preprocess -> index flow.

Implementation platform:
- Scheduler is implemented using **GitHub Actions** (`cron`-based workflow).
- Workflow triggers the scraping and ingestion jobs and records run status artifacts.

Schedule configuration:
- Frequency: daily
- Time: 09:15
- Timezone: IST (`Asia/Kolkata`)

Operational notes:
- If a scheduled run fails, trigger retry with backoff and alerting.
- Maintain `scheduler_runs` logs with start time, end time, status, and triggered batch ID.

GitHub Actions notes:
- Use UTC cron with IST mapping for the 09:15 run.
- Use concurrency control to prevent overlapping runs.
- Store run logs/metrics as workflow artifacts and push execution status to observability store.

## 4.0.1 Scraping Service

Responsibilities:
- Fetch data from all configured corpus URLs.
- Extract relevant textual content from AMC and scheme pages.
- Clean and preprocess raw HTML content.
- Prepare normalized text payloads for chunking and embedding.

Implementation notes:
- Inputs: URL list from `source_registry`.
- Outputs: cleaned document payloads with URL, title, fetch timestamp, and content hash.
- Failures: mark per-URL status and continue remaining URLs (partial progress support).

## 4.1 Source Intake Layer

Responsibilities:
- Accept only URLs from `groww.in/mutual-funds/*` for this phase.
- Maintain `source_registry` with URL, domain, source type, scheme tags, and fetch schedule.
- Track crawl status, checksum/hash, and last fetch timestamp.

Key controls:
- Domain allowlist enforced at ingestion.
- Reject non-Groww domains at onboarding time.
- Robots and rate-limit compliant fetching.

Suggested entities:
- `sources(id, url, domain, source_type, amc, scheme, category, active)`
- `source_fetch_runs(source_id, fetched_at, status, checksum, http_status)`

## 4.2 Document Processing and Normalization Layer

Pipeline:
- Fetch -> Parse -> Clean -> Segment -> Enrich -> Store.

Parsing:
- HTML pages only (AMC pages and scheme pages from Groww).
- PDF parsing is disabled in current scope.

Normalization:
- Remove boilerplate/navigation.
- Preserve factual units (fees, loads, benchmark, dates).
- Normalize monetary units and percentages for consistent retrieval.

Chunking strategy:
- Hybrid chunking: section-aware + token window.
- Target size: 300-700 tokens with 10-15% overlap.
- Metadata attached per chunk:
  - `source_url`
  - `document_type` (groww_amc_page/groww_scheme_page)
  - `scheme_name`
  - `amc_name`
  - `as_of_date`
  - `effective_date`
  - `section_title`
  - `last_crawled_at`

## 4.3 Indexing Layer

Vector database: **ChromaDB** ([trychroma.com](https://www.trychroma.com))

ChromaDB is used as the unified index layer, replacing the previous separate FAISS + BM25 + metadata JSON approach. It provides vector search, metadata filtering, and full-text search in a single embedded database.

### Why ChromaDB over FAISS + BM25

| Concern | FAISS + BM25 (previous) | ChromaDB (current) |
|---|---|---|
| Vector search | FAISS flat index (separate `.faiss` file) | Built-in vector index with HNSW |
| Keyword search | Separate BM25 pickle file | Built-in full-text search via `where_document` |
| Metadata filtering | Separate `metadata.json` file | Native metadata filters (`where` clause) |
| Upsert / dedup | Manual by `chunk_id` lookup | Native upsert by document ID |
| Persistence | Three separate files to keep in sync | Single persistent directory (`data/chroma/`) |
| Embedding function | Manual `sentence-transformers` encode calls | Pluggable embedding functions (using `bge-base-en-v1.5`) |

### Collection design

- **Collection name:** `groww_mf_chunks`
- **Embedding model:** `BAAI/bge-base-en-v1.5` (768 dimensions), configured via ChromaDB's `SentenceTransformerEmbeddingFunction`
- **Distance metric:** Cosine similarity

Each document in the collection maps to one chunk and stores:
- `id`: chunk UUID (used as ChromaDB document ID for native upsert)
- `documents`: the chunk text
- `metadatas`: structured metadata per chunk (`source_url`, `amc_name`, `scheme_name`, `document_type`, `fetched_at`, `content_hash`, `pipeline_version`, `embedding_model_version`)

### Query-time capabilities

- **Semantic search:** `collection.query(query_texts=[...], n_results=k)`
- **Metadata filtering:** `where={"amc_name": "SBI"}` or `where={"document_type": "groww_scheme_page"}`
- **Full-text filtering:** `where_document={"$contains": "expense ratio"}` for exact phrase match
- **Combined:** All three can be composed in a single query call

### Index design
- Chunk-level embeddings (ChromaDB handles embedding generation internally via the configured embedding function).
- Optional title+chunk dual embeddings for better section recall.
- Metadata filters at query time:
  - scheme-specific constraints
  - document recency preference
  - source ranking (scheme page > AMC listing page for scheme-specific values)

## 4.4 Retrieval and Re-ranking Layer

Query flow:
1. Intent classification (factual vs advisory/prohibited vs out-of-scope).
2. Query rewriting (expand scheme aliases, normalize terms like "ER" -> "expense ratio").
3. Hybrid retrieval (ChromaDB semantic query + full-text `where_document` filter, top-k results).
4. Metadata filtering (Groww source, relevant scheme/doc type).
5. Re-ranking (cross-encoder or lightweight reranker).
6. Evidence packing (top 3-5 chunks max).

Retrieval quality rules:
- Prefer latest valid source for time-sensitive values.
- If conflicting values across docs, choose most recent official effective date and mention date in output.
- If confidence below threshold, return clarification prompt or "not found in official corpus."

## 4.5 Grounded Answer Generation Layer

Prompt contract:
- Answer using retrieved evidence only.
- Maximum 3 sentences.
- Neutral tone; no prescriptive language.
- Include exactly one citation in response body.
- Add footer: `Last updated from sources: <date>`.

Answer template:
- Sentence 1: direct factual answer.
- Sentence 2: qualifying condition/date/context.
- Sentence 3: optional brief process step (if procedural query).
- Citation: `[Source: <title/domain>]`
- Footer date from most recent cited evidence timestamp.

Hallucination prevention:
- "No evidence, no answer" rule.
- Generator receives only selected chunks + schema-constrained instructions.
- Post-generation verifier checks claim-to-evidence match.

## 4.6 Policy and Safety Guardrail Layer

Pre-generation guardrails:
- Detect prohibited intents:
  - investment advice
  - recommendation/ranking
  - return comparison/calculation
- Trigger refusal template with AMFI/SEBI educational link.

PII guardrails:
- Detect and block sensitive data in user input/output:
  - PAN, Aadhaar, bank details, OTPs, phone, email.
- Respond with safe message and do not store sensitive payloads.

Post-generation guardrails:
- Ensure:
  - sentence count <= 3
  - citation present
  - footer present
  - no advisory language
- If failed, auto-rewrite or return safe fallback.

## 4.7 API and Multi-Thread Chat Layer

Endpoints (example):
- `POST /chat/{thread_id}/query`
- `POST /threads`
- `GET /threads/{thread_id}/history`
- `GET /health`

Thread model:
- Independent thread context and minimal memory.
- Context carries:
  - selected AMC/scheme hints
  - prior factual entities
  - latest successful citation context

Important constraint:
- Thread memory can improve query disambiguation, but retrieval remains mandatory for each response.

## 4.8 UI Layer Requirements

Must include:
- Welcome message.
- Three example factual questions.
- Persistent disclaimer banner: `Facts-only. No investment advice.`

Response UX:
- Show answer + citation + last-updated footer.
- For refusals: clear reason + allowed alternative + official educational link.

## 4.9 Observability, Logging, and Compliance

Log per request:
- query class (factual/advisory/refusal)
- retrieval candidates and selected chunk IDs
- citation URL
- guardrail pass/fail
- latency breakdown (retrieve/rerank/generate/verify)

Dashboards:
- factual answer rate
- refusal correctness rate
- citation coverage (% with valid official citation)
- freshness lag (days since last crawl)
- unsupported query categories

Retention and privacy:
- redact sensitive user content in logs.
- store only necessary telemetry for debugging and evaluation.

## 5) Data Model (Reference)

- `documents(id, source_id, title, document_type, published_at, effective_date, raw_path, parsed_path)`
- `chunks(id, document_id, chunk_text, section_title, token_count, embedding, metadata_json)`
- `threads(id, created_at, user_context_json)`
- `messages(id, thread_id, role, content, created_at, policy_flags_json)`
- `query_runs(id, message_id, intent, retrieval_json, generation_json, verdict, created_at)`

## 6) End-to-End Request Sequence

1. Scheduler triggers scraping service daily at 09:15 IST.
2. Scraping service fetches and processes configured Groww URLs.
3. Processed data is passed to ingestion/chunking/embedding and then indexed.
4. User asks question.
5. Intent and policy classifier runs.
6. If prohibited -> refusal response.
7. If factual -> query expansion + hybrid retrieval.
8. Re-rank and pack evidence.
9. Generate concise grounded answer.
10. Verify policy/citation/format constraints.
11. Return response with citation and last-updated footer.
12. Persist telemetry and metrics.

## 7) Non-Functional Requirements

- **Accuracy:** prioritize precision over recall for factual finance content.
- **Latency target:** p95 <= 2.5-3.5s for standard query load.
- **Availability:** 99.5%+ for API service.
- **Scalability:** stateless API with horizontally scalable retrieval/generation workers.
- **Security:** allowlist-only ingestion, strict input validation, PII redaction.

## 8) Evaluation Framework

Offline evaluation set:
- 150-300 curated QA pairs across supported topics.
- 30-50 prohibited/advisory queries.
- 20-30 ambiguity and "not found" queries.

Metrics:
- Retrieval Recall@k and MRR.
- Grounded factual accuracy (human-verified).
- Citation correctness (URL/domain/claim alignment).
- Refusal precision/recall for prohibited intents.
- Format compliance (3-sentence cap, footer, citation).

Acceptance thresholds (recommended):
- Citation correctness >= 98%
- Advisory refusal precision >= 99%
- Format compliance >= 99%
- Hallucination rate <= 1%

## 9) Refresh and Update Strategy

Cadence:
- Scheduler-driven daily refresh at 09:15 IST.
- Daily incremental checks for URL changes (executed within scheduled run).
- Weekly full re-parse/re-index.
- Immediate re-index for high-impact source updates.

Change handling:
- Version snapshots of chunks and indices.
- Atomic index swap to prevent mixed-version retrieval.
- Alerting on extraction failures or schema drift.

## 10) Deployment Blueprint

Services:
- `scheduler-service` (implemented via GitHub Actions, daily trigger at 09:15 IST)
- `scraping-service` (fetch, extract, clean, preprocess)
- `ingestion-worker`
- `parser-normalizer`
- `indexer`
- `retrieval-api`
- `policy-engine`
- `chat-api`
- `monitoring-stack`

Infrastructure:
- Object storage for raw/parsed docs.
- ChromaDB (persistent mode) for vector search, metadata filtering, and full-text search.
- Relational DB for metadata, threads, and telemetry.
- Queue for asynchronous crawling/indexing.

Environments:
- `dev` -> `staging` -> `prod` with source allowlist and policy rules promoted via controlled config.

## 10.1) Chunking and Embedding Architecture (Separate Detailed Design)

This section defines the dedicated processing architecture between scraping output and vector index updates.

### A) Inputs and Preconditions

Input payload from scraping service (per URL):
- `url`
- `title`
- `amc_name`
- `scheme_name` (nullable for AMC pages)
- `document_type` (`groww_amc_page` or `groww_scheme_page`)
- `fetched_at`
- `content_hash`
- `clean_text`

Preconditions:
- URL must match Groww allowlist.
- `clean_text` length must pass minimum content threshold.
- Duplicate content (`content_hash`) is skipped unless forced re-embed is enabled.

### B) Chunking Pipeline

1. **Section detection**
- Identify logical boundaries from headings, labels, and table-like blocks.
- Preserve high-signal sections such as expense ratio, exit load, benchmark, risk, and fund overview.

2. **Semantic-preserving split**
- Split text into chunks of 300-700 tokens.
- Apply 10-15% overlap to preserve context across boundaries.
- Ensure value+unit pairs stay in same chunk (for example percentages and amounts).

3. **Chunk normalization**
- Remove residual boilerplate and repeated disclaimers.
- Normalize whitespace, punctuation, and list formatting.
- Preserve exact numeric values and dates without transformation.

4. **Chunk scoring and filtering**
- Drop low-information chunks (navigation remnants, legal noise, duplicate snippets).
- Keep high-relevance chunks using keyword and structure heuristics.

Output schema per chunk:
- `chunk_id`
- `document_id`
- `chunk_text`
- `token_count`
- `chunk_index`
- `section_title`
- `metadata_json`

### C) Metadata Enrichment Standard

`metadata_json` fields:
- `source_url`
- `domain` (`groww.in`)
- `document_type`
- `amc_name`
- `scheme_name`
- `as_of_date` (if detected)
- `effective_date` (if detected)
- `last_crawled_at`
- `content_hash`
- `pipeline_version`
- `embedding_model_version`

Metadata rules:
- `scheme_name` is mandatory for scheme pages.
- `as_of_date` and `effective_date` are optional but parsed when available.
- `pipeline_version` tracks chunking logic evolution for reproducibility.

### D) Embedding Pipeline

1. **Model selection**
- Use one production embedding model for consistency.
- Lock model version to avoid vector-space drift during normal runs.

2. **Batch embedding**
- Process chunks in controlled batches (for throughput and retry safety).
- Use idempotent upsert keys: `document_id + chunk_index + pipeline_version`.

3. **Vector quality checks**
- Reject embeddings with invalid dimensions or NaN values.
- Track embedding generation latency, failure rate, and retry count.

4. **Storage**
- Upsert chunks into ChromaDB collection (`groww_mf_chunks`) with `collection.upsert()`.
- ChromaDB stores vectors, documents, and metadata atomically per chunk — no separate sync needed.
- Persistence directory: `data/chroma/`.

### E) Re-Embedding and Versioning Strategy

Triggers for re-embedding:
- Content hash changed.
- Chunking pipeline version changed.
- Embedding model version changed.

Versioning approach:
- Maintain `active_index_version`.
- Build new vectors in a staging namespace/index.
- Perform atomic swap to production index after validation.
- Retain previous index version for rollback.

### F) Validation and Acceptance Gates

Chunk-level gates:
- token range compliance (300-700 preferred).
- overlap compliance (10-15%).
- required metadata presence.

Embedding-level gates:
- dimension consistency.
- successful upsert confirmation.
- index-document count parity check.

Run-level gates:
- minimum successful URL coverage threshold.
- minimum chunk generation threshold.
- fail run if critical sections are missing across all scheme pages.

### G) Operational Flow with GitHub Actions Scheduler

1. GitHub Actions cron triggers daily ingestion workflow at 09:15 IST.
2. Workflow starts scraping service for configured Groww URLs.
3. Scraped documents pass through chunking pipeline.
4. Chunks are embedded and upserted to ChromaDB collection in batches.
5. Validation gates execute.
6. If all checks pass, new index version is activated.
7. Workflow publishes metrics and status notifications.

### H) Failure Handling

- Per-URL retry with exponential backoff.
- Per-batch embedding retry with dead-letter capture for persistent failures.
- Partial indexing allowed only if coverage threshold is met; else run is marked failed.
- Automatic alert on failed scheduled run or stale index age breach.

## 11) Refusal and Fallback Templates

Refusal example:
"I can only help with factual information available in the current Groww source corpus and cannot provide investment advice or comparisons."

Low-confidence factual fallback:
"I could not find a verifiable answer in the current Groww source corpus for this scheme. Please check the relevant scheme page URL."

## 12) Known Risks and Mitigations

- **Risk:** stale scheme page values.
  - **Mitigation:** freshness checks + visible last-updated footer + scheduled recrawl.
- **Risk:** missing fields that exist only in PDF disclosures.
  - **Mitigation:** explicit "out of current scope" handling and planned PDF ingestion in next phase.
- **Risk:** subtle advisory phrasing by model.
  - **Mitigation:** pre/post guardrails + constrained generation + refusal classifier.
- **Risk:** conflicting values across documents.
  - **Mitigation:** effective-date precedence and source hierarchy rules.

## 13) MVP vs Phase 2

MVP:
- 4 AMCs with the curated 15 Groww URLs listed in this document.
- Hybrid retrieval, one citation, policy refusals.
- Multi-thread chat and basic observability.

Phase 2:
- Multi-AMC expansion.
- Better table extraction and field-level validation.
- Automated conflict resolution explainability.
- Continuous evaluation and active learning loops.

