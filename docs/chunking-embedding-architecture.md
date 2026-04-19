# Chunking and Embedding Architecture (Phase 4 & 5)

This document defines the dedicated processing architecture between scraping output and vector index updates, specifically optimized for the **bge-base-en-v1.5** model and stored via **ChromaDB**.

## 1. Overview
The transition from raw scraped documents to vectorized chunks is a critical step in ensuring high retrieval precision. This phase focuses on semantic preservation and metadata richness.

## 2. Core Model: bge-base-en-v1.5
We have selected **bge-base-en-v1.5** as the primary embedding model for this project, replacing the generic OpenAI models.
- **Provider:** HuggingFace / Local Execution
- **Dimensions:** 768
- **Context Window:** 512 tokens
- **Strengths:** Optimized for retrieval tasks (Retrieval-Augmented Generation).

## 3. Vector Store: ChromaDB
We use **ChromaDB** ([trychroma.com](https://www.trychroma.com)) as the unified vector store, replacing the previous FAISS + BM25 + metadata JSON approach.

- **Collection name:** `groww_mf_chunks`
- **Persistence:** Local persistent directory at `data/chroma/`
- **Embedding function:** `SentenceTransformerEmbeddingFunction` with `BAAI/bge-base-en-v1.5`
- **Distance metric:** Cosine similarity

### Advantages over FAISS + BM25
- **Single system:** Vector search, full-text search, and metadata filtering in one database — no file sync issues.
- **Native upsert:** Deduplication by chunk ID handled automatically by `collection.upsert()`.
- **Query-time filtering:** `where` (metadata) and `where_document` (full-text) filters compose naturally with semantic search.
- **No manual serialization:** No `.faiss`, `.pkl`, or `.json` files to manage separately.

## 4. Chunking Pipeline logic
1.  **Semantic-Aware Splitting:** Chunks are split at paragraph boundaries rather than arbitrary character counts.
2.  **Size Constraints:** Target chunk size is ~400-500 words (matching the model's token limit).
3.  **Context Overlap:** 10-15% overlap (~50 words) to prevent losing context across boundaries.
4.  **Metadata Preservation:** Every chunk carries its source URL, AMC name, and scheme name.

## 5. Metadata Standard
Each chunk upserted into the ChromaDB collection MUST include:
- `id`: chunk UUID (used as ChromaDB document ID)
- `documents`: chunk text content
- `metadatas`:
  - `document_id`: Reference to parent document
  - `source_url`
  - `amc_name`
  - `scheme_name`
  - `document_type`
  - `fetched_at`
  - `content_hash`
  - `embedding_model_version`: "bge-base-en-v1.5"
  - `pipeline_version`: "phase-4-v1"

## 6. Implementation Roadmap
- [x] Update `processor.py` to include Model Version in metadata.
- [x] Implement `indexer.py` (Phase 5) using `sentence-transformers`.
- [x] Validate vector dimensions on the first batch of 242 chunks.
- [x] Migrate `indexer.py` from FAISS + BM25 to ChromaDB.
- [x] Validate ChromaDB collection count matches 242 chunks.
- [x] Update retrieval layer to use ChromaDB query API.
