"""
Phase 4.3 -- Indexing Layer (ChromaDB Local + Cloud)

Implements section 4.3 + 10.1-D/E/F of rag-architecture.md:
  - ChromaDB CloudClient (if CHROMA_API_KEY is set) OR PersistentClient (local fallback)
  - Collection: groww_mf_chunks
  - Embedding: BAAI/bge-base-en-v1.5 via SentenceTransformerEmbeddingFunction
  - Idempotent upsert key: document_id::chunk_index::pipeline_version
  - Batch upsert with retry
  - Vector quality checks (dimension, NaN)
  - Validation gates (count parity, metadata presence)
  - Run summary logging
"""

import json
import os
import pathlib
import sys
import time
import datetime as dt
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
from fastembed import TextEmbedding
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────────────────────────
load_dotenv(pathlib.Path(__file__).resolve().parents[3] / ".env")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "data" / "processed" / "latest" / "chunks.json"
CHROMA_LOCAL_DIR = ROOT / os.getenv("CHROMA_DB_DIR", "data/chroma")
RUN_LOG_DIR = ROOT / "data" / "index"

# ── ChromaDB Cloud config ─────────────────────────────────────────────────────
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "").strip()
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "").strip()
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "").strip()

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
VECTOR_DIMENSION = 384
# Priority: .env > hardcoded default
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "groww_mf_chunks_v4")
print(f"[indexer] TARGET COLLECTION: {COLLECTION_NAME}")
BATCH_SIZE = 50           # controlled batch size for throughput and retry safety
MAX_RETRIES = 3           # per-batch retry count

# ── Required metadata keys per architecture spec (section C) ───────────────────
REQUIRED_META_KEYS = {"source_url", "document_type", "amc_name", "content_hash"}


# ===========================================================================
# 1. Data Loading
# ===========================================================================
def _load_chunks():
    """Load processed chunks from the latest pipeline run."""
    if not INPUT_PATH.exists():
        print(f"[indexer] ERROR  {INPUT_PATH} not found.")
        sys.exit(1)
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    chunks = data.get("chunks", [])
    if not chunks:
        print("[indexer] ERROR  No chunks found in payload.")
        sys.exit(1)
    return chunks


# ===========================================================================
# 2. ChromaDB Client Factory (Cloud vs Local)
# ===========================================================================
def _create_chroma_client():
    """
    If CHROMA_API_KEY is configured, connect to ChromaDB Cloud.
    Otherwise fall back to local PersistentClient.
    Returns (client, mode_label).
    """
    if CHROMA_API_KEY:
        print("[indexer] Connecting to ChromaDB Cloud...")
        kwargs = {"api_key": CHROMA_API_KEY}
        if CHROMA_TENANT:
            kwargs["tenant"] = CHROMA_TENANT
        if CHROMA_DATABASE:
            kwargs["database"] = CHROMA_DATABASE
        client = chromadb.CloudClient(**kwargs)
        return client, "cloud"
    else:
        CHROMA_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[indexer] Using local ChromaDB at {CHROMA_LOCAL_DIR}")
        client = chromadb.PersistentClient(path=str(CHROMA_LOCAL_DIR))
        return client, "local"


# ===========================================================================
# 3. Idempotent ID Generation  (spec 10.1-D-2)
# ===========================================================================
def _make_upsert_id(chunk: dict) -> str:
    """
    Idempotent upsert key = document_id + chunk_index + pipeline_version.
    Ensures that re-running the indexer on the same data is a no-op,
    while a pipeline_version bump triggers re-embedding.
    """
    doc_id = chunk.get("document_id", "unknown")
    idx = chunk.get("chunk_index", 0)
    pv = chunk.get("pipeline_version", "phase-4-v1")
    return f"{doc_id}::{idx}::{pv}"


# ===========================================================================
# 4. Metadata Flattening  (spec 4.3 + 10.1-C)
# ===========================================================================
def _flatten_metadata(chunk: dict) -> dict:
    """
    Build a flat metadata dict for ChromaDB from the nested chunk structure.
    ChromaDB metadata values must be str | int | float | bool.
    """
    meta = chunk.get("metadata", {})
    return {
        "document_id":             str(chunk.get("document_id", "")),
        "chunk_index":             int(chunk.get("chunk_index", 0)),
        "token_count_est":         int(chunk.get("token_count_est", 0)),
        "source_url":              str(meta.get("source_url", "")),
        "domain":                  str(meta.get("domain", "groww.in")),
        "document_type":           str(meta.get("document_type", "")),
        "amc_name":                str(meta.get("amc_name", "")),
        "scheme_name":             str(meta.get("scheme_name") or ""),
        "as_of_date":              str(meta.get("as_of_date") or ""),
        "effective_date":          str(meta.get("effective_date") or ""),
        "fetched_at":              str(meta.get("fetched_at", "")),
        "last_crawled_at":         str(meta.get("last_crawled_at") or meta.get("fetched_at", "")),
        "content_hash":            str(meta.get("content_hash", "")),
        "pipeline_version":        str(chunk.get("pipeline_version", "phase-4-v1")),
        "embedding_model_version": str(chunk.get("embedding_model_version", MODEL_NAME)),
    }


# ===========================================================================
# 5. Validation Gates  (spec 10.1-F)
# ===========================================================================
def _validate_metadata_presence(chunks: list) -> list:
    """
    Chunk-level gate: ensure required metadata keys are present.
    Returns list of warning strings (empty = all good).
    """
    warnings = []
    for i, chunk in enumerate(chunks):
        meta = chunk.get("metadata", {})
        missing = REQUIRED_META_KEYS - set(meta.keys())
        if missing:
            warnings.append(f"  chunk {i} ({chunk.get('chunk_id','?')}): missing {missing}")
    return warnings


def _validate_embeddings(model, texts: List[str]):
    """Computes embeddings using fastembed and checks for validity."""
    print(f"[indexer] Computing embeddings for {len(texts)} chunks...")
    t0 = time.perf_counter()
    embeddings = np.array(list(model.embed(texts)))
    elapsed = time.perf_counter() - t0
    print(f"[indexer] Embeddings computed in {elapsed:.2f}s ({len(texts)/elapsed:.1f} chunks/s)")

    # Dimension check
    if embeddings.shape[1] != VECTOR_DIMENSION:
        print(f"[indexer] FATAL  Embedding dimension {embeddings.shape[1]} != expected {VECTOR_DIMENSION}")
        sys.exit(1)

    # NaN check
    nan_mask = np.isnan(embeddings).any(axis=1)
    nan_count = int(nan_mask.sum())
    if nan_count > 0:
        print(f"[indexer] WARNING  {nan_count} embeddings contain NaN -- these chunks will be skipped.")

    return embeddings, nan_mask, elapsed


# ===========================================================================
# 6.  Main Build Pipeline
# ===========================================================================
def build_indices():
    run_start = time.perf_counter()
    run_ts = dt.datetime.now(dt.timezone.utc).isoformat()
    print(f"[indexer] === Indexing Layer (Phase 4.3) ===  {run_ts}")
    print(f"[indexer] VERSION: v_PartialSuccess_80_Final")

    # ── 6a. Load data ──────────────────────────────────────────────────────────
    chunks = _load_chunks()
    total_chunks = len(chunks)
    print(f"[indexer] Loaded {total_chunks} chunks from {INPUT_PATH}")

    # ── 6b. Metadata presence validation ──────────────────────────────────────
    meta_warnings = _validate_metadata_presence(chunks)
    if meta_warnings:
        print(f"[indexer] WARNING  {len(meta_warnings)} chunks have missing metadata:")
        for w in meta_warnings[:10]:
            print(w)

    # ── 6c. Prepare texts, ids, metadata ──────────────────────────────────────
    texts = []
    ids = []
    metadatas = []
    for chunk in chunks:
        texts.append(chunk["chunk_text"])
        ids.append(_make_upsert_id(chunk))
        metadatas.append(_flatten_metadata(chunk))

    # ── 6d. Compute & validate embeddings ─────────────────────────────────────
    print(f"[indexer] Initializing fastembed model {MODEL_NAME}...")
    model = TextEmbedding(
        model_name=f"sentence-transformers/{MODEL_NAME}", 
        cache_dir=str(ROOT / "data" / "fastembed_cache")
    )
    embeddings, nan_mask, embed_elapsed = _validate_embeddings(model, texts)

    # Filter out NaN rows
    valid_indices = [i for i in range(len(ids)) if not nan_mask[i]]
    if len(valid_indices) < len(ids):
        ids        = [ids[i]        for i in valid_indices]
        texts      = [texts[i]      for i in valid_indices]
        metadatas  = [metadatas[i]  for i in valid_indices]
        embeddings = embeddings[valid_indices]
        print(f"[indexer] Proceeding with {len(ids)} valid chunks (dropped {total_chunks - len(ids)})")

    # ── 6e. ChromaDB setup (Cloud or Local) ───────────────────────────────────
    client, mode = _create_chroma_client()
    print(f"[indexer] ChromaDB mode: {mode}")

    # For cloud mode, ChromaDB Cloud handles embeddings server-side when using
    # SentenceTransformerEmbeddingFunction. But since we pre-compute embeddings
    # locally (for quality validation), we pass them directly in upsert().
    # The embedding_function is registered so query-time works seamlessly.
    print("###################################################")
    print(f"LOG CHECK: TARGETING COLLECTION '{COLLECTION_NAME}'")
    print("###################################################")

    # Custom wrapper for FastEmbed to ensure compatibility with all Chroma versions
    class SuperLighterSearch:
        def __init__(self, model):
            self.model = model
        def name(self):
            return "all-MiniLM-L6-v2"
        def __call__(self, input):
            if isinstance(input, str):
                input = [input]
            return list(self.model.embed(list(input)))
        def embed_query(self, input):
            return self(input)
        def embed_documents(self, input):
            return self(input)

    fastembed_ef = SuperLighterSearch(model=model)

    # ── 6e. Robust Collection Acquisition ──────────────────────────────────
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=fastembed_ef,
            metadata={"hnsw:space": "cosine"},
        )
    except ValueError as ve:
        # This catch handles the "embedding function already exists... and a new one is provided" conflict
        print(f"[indexer] VALUE ERROR: {ve}")
        print(f"[indexer] Conflict detected for '{COLLECTION_NAME}'. Wiping and recreating...")
        try:
            client.delete_collection(name=COLLECTION_NAME)
            collection = client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=fastembed_ef,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            print(f"[indexer] FATAL: Could not resolve collection conflict: {e}")
            sys.exit(1)
    print(f"[indexer] Collection '{COLLECTION_NAME}' ready (existing count: {collection.count()})")

    # ── 6f. Upsert with retry (spec 10.1-D-2 & H) ─────────────────────────────
    # Cloud free tier limits document size per upsert (~16KB).
    # Use single-document upserts for cloud; batch upserts for local (faster).
    upserted = 0
    failed_items = []

    if mode == "cloud":
        # ── Cloud: one-by-one upsert ──────────────────────────────────────────
        for idx in range(len(ids)):
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    collection.upsert(
                        ids=[ids[idx]],
                        documents=[texts[idx]],
                        metadatas=[metadatas[idx]],
                        embeddings=[embeddings[idx].tolist()],
                    )
                    upserted += 1
                    break
                except Exception as exc:
                    if attempt == MAX_RETRIES:
                        failed_items.append((idx, ids[idx], str(exc)))
                    else:
                        time.sleep(1 * attempt)

            if (idx + 1) % 25 == 0 or idx == len(ids) - 1:
                print(f"[indexer] Cloud upsert progress: {idx + 1}/{len(ids)}  (ok: {upserted}, failed: {len(failed_items)})")
    else:
        # ── Local: batch upsert ───────────────────────────────────────────────
        for start in range(0, len(ids), BATCH_SIZE):
            end = min(start + BATCH_SIZE, len(ids))
            batch_num = start // BATCH_SIZE + 1

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    collection.upsert(
                        ids=ids[start:end],
                        documents=texts[start:end],
                        metadatas=metadatas[start:end],
                        embeddings=embeddings[start:end].tolist(),
                    )
                    upserted += (end - start)
                    print(f"[indexer] Batch {batch_num} upserted ({end - start} chunks)")
                    break
                except Exception as exc:
                    print(f"[indexer] WARNING  Batch {batch_num} attempt {attempt}/{MAX_RETRIES} failed: {exc}")
                    if attempt == MAX_RETRIES:
                        failed_items.append((start, end, str(exc)))
                        print(f"[indexer] ERROR  Batch {batch_num} dead-lettered after {MAX_RETRIES} retries.")
                    else:
                        time.sleep(1 * attempt)

    # ── 6g. Count parity check (spec 10.1-F) ─────────────────────────────────
    final_count = collection.count()
    print(f"[indexer] Collection count after upsert: {final_count}")
    if final_count < len(ids):
        print(f"[indexer] INFO: Partial indexing detected -- Found {final_count} items in collection, expected {len(ids)}.")

    # ── 6h. Handle Partial Success Logic  (User Specification) ────────────────
    success_rate = 0.0
    if total_chunks > 0:
        success_rate = upserted / total_chunks
    
    status = "SUCCESS"
    exit_code = 0
    
    if success_rate < 0.8:
        status = "FAILURE"
        exit_code = 1
    elif success_rate < 1.0:
        status = "PARTIAL SUCCESS"
        exit_code = 0

    print(f"\n[indexer] Status: {status}")
    print(f"[indexer] Indexed: {upserted}/{total_chunks}")
    print(f"[indexer] Success Rate: {success_rate:.1%}")

    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    if failed_items:
        failed_path = RUN_LOG_DIR / "failed-items.json"
        print(f"[indexer] Logging {len(failed_items)} failures to {failed_path}")
        failed_payload = [
            {"chunk_id": f[1], "error_reason": f[2]}
            for f in failed_items
        ]
        with failed_path.open("w", encoding="utf-8") as f:
            json.dump(failed_payload, f, indent=2)

    # ── 6i. Run summary ──────────────────────────────────────────────────────
    run_elapsed = time.perf_counter() - run_start
    summary = {
        "run_timestamp":       run_ts,
        "status":              status,
        "success_rate":        round(success_rate, 4),
        "chroma_mode":         mode,
        "model_name":          MODEL_NAME,
        "vector_dimension":    VECTOR_DIMENSION,
        "collection_name":     COLLECTION_NAME,
        "input_chunks":        total_chunks,
        "valid_chunks":        len(ids),
        "upserted_chunks":     upserted,
        "failed_chunks":       len(failed_items),
        "final_collection_count": final_count,
        "total_latency_s":     round(run_elapsed, 2),
    }

    summary_path = RUN_LOG_DIR / "latest-index-run.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[indexer] === Done === Exit Code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    build_indices()
