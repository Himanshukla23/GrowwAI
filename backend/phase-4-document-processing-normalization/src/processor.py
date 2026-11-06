import datetime as dt
import json
import pathlib
import sys
import uuid
from typing import Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[3]
DOCUMENTS_PATH = ROOT / "data" / "processed" / "latest" / "documents.json"
OUTPUT_PATH = ROOT / "data" / "processed" / "latest" / "chunks.json"

# Configuration
CHUNK_TARGET_WORDS = 400  # Approx 500-600 tokens
CHUNK_OVERLAP_WORDS = 50   # Approx 10-15% overlap
PIPELINE_VERSION = "phase-4-v1"
EMBEDDING_MODEL = "bge-base-en-v1.5"



def _load_documents() -> Dict:
    if not DOCUMENTS_PATH.exists():
        print(f"[processor] Error: {DOCUMENTS_PATH} not found.")
        sys.exit(1)
    with DOCUMENTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _split_into_chunks(text: str, target_size: int, overlap: int) -> List[str]:
    # 1. Clean paragraphs and pre-split any paragraph that exceeds target_size
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    paragraphs = []
    for p in raw_paragraphs:
        words = p.split()
        if len(words) <= target_size:
            paragraphs.append(p)
        else:
            step = target_size - overlap if target_size > overlap else target_size
            for idx in range(0, len(words), step):
                slice_words = words[idx : idx + target_size]
                if slice_words:
                    paragraphs.append(" ".join(slice_words))
    
    chunks = []
    current_chunk_paragraphs = []
    current_word_count = 0
    
    for p in paragraphs:
        p_word_count = len(p.split())
        
        # If adding this paragraph exceeds target and we already have content
        if current_word_count + p_word_count > target_size and current_chunk_paragraphs:
            # Finalize current chunk
            chunks.append("\n".join(current_chunk_paragraphs))
            
            # Start new chunk with overlap
            # We take the last few paragraphs that sum up to roughly 'overlap' words
            overlap_paragraphs = []
            o_words = 0
            for op in reversed(current_chunk_paragraphs):
                op_words = len(op.split())
                if o_words + op_words <= overlap:
                    overlap_paragraphs.insert(0, op)
                    o_words += op_words
                else:
                    break
            
            current_chunk_paragraphs = overlap_paragraphs + [p]
            current_word_count = o_words + p_word_count
        else:
            current_chunk_paragraphs.append(p)
            current_word_count += p_word_count
            
    if current_chunk_paragraphs:
        chunks.append("\n".join(current_chunk_paragraphs))
        
    # 2. Hard byte-size safeguard: ChromaDB Cloud limit is 16,384 bytes
    safe_chunks = []
    max_bytes = 12000
    for ch in chunks:
        ch_bytes = ch.encode("utf-8")
        if len(ch_bytes) <= max_bytes:
            safe_chunks.append(ch)
        else:
            words = ch.split()
            step = 300
            for idx in range(0, len(words), 250):
                sub_ch = " ".join(words[idx : idx + step])
                if sub_ch.strip():
                    safe_chunks.append(sub_ch)
                    
    return safe_chunks


def process_documents() -> None:
    data = _load_documents()
    documents = data.get("documents", [])
    all_chunks = []
    
    print(f"[processor] Processing {len(documents)} documents...")
    
    for doc in documents:
        text = doc.get("clean_text", "")
        if not text:
            continue
            
        # 1. Splitting
        raw_chunks = _split_into_chunks(text, CHUNK_TARGET_WORDS, CHUNK_OVERLAP_WORDS)
        
        # 2. Enrichment & Normalization
        scheme_prefix = ""
        if doc.get("scheme_name"):
            scheme_prefix = f"[Scheme: {doc.get('scheme_name')} | AMC: {doc.get('amc_name', '')}]\n"

        for i, chunk_text in enumerate(raw_chunks):
            # Prepend contextual header if not already present
            final_text = chunk_text
            if scheme_prefix and not chunk_text.startswith("===") and not chunk_text.startswith("[Scheme:"):
                final_text = scheme_prefix + chunk_text

            # Calculate token count (approx)
            word_count = len(final_text.split())
            token_est = int(word_count / 0.75)
            
            chunk_payload = {
                "chunk_id": str(uuid.uuid4()),
                "document_id": doc.get("document_id"),
                "chunk_index": i,
                "chunk_text": final_text,
                "token_count_est": token_est,
                "pipeline_version": PIPELINE_VERSION,
                "embedding_model_version": EMBEDDING_MODEL,
                "metadata": {
                    "source_url": doc.get("url"),
                    "domain": doc.get("domain"),
                    "document_type": doc.get("document_type"),
                    "amc_name": doc.get("amc_name"),
                    "scheme_name": doc.get("scheme_name"),
                    "fetched_at": doc.get("fetched_at"),
                    "content_hash": doc.get("content_hash")
                }
            }
            all_chunks.append(chunk_payload)
            
    # 3. Storage
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump({
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "total_documents": len(documents),
            "total_chunks": len(all_chunks),
            "chunks": all_chunks
        }, f, indent=2, ensure_ascii=True)
        
    print(f"[processor] Done. Generated {len(all_chunks)} chunks.")


if __name__ == "__main__":
    process_documents()
