import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "phase-6-retrieval-reranking-layer" / "src"))
from retriever import Retriever
from pipeline import RetrievalPipeline

r = Retriever()
p = RetrievalPipeline(r)
res = p.run("What is the expense ratio of SBI Contra Fund?")
print(f"Total chunks retrieved: {len(res.get('raw_results', []))}")
for i, chunk in enumerate(res.get("raw_results", [])[:5]):
    meta = chunk.get("metadata", {})
    print(f"Chunk {i+1}: {meta.get('amc_name')} | {meta.get('scheme_name')} | Score: {chunk.get('rerank_score'):.4f}")
    # Print a snippet safely
    text = chunk.get("text", "")[:100].replace("\u20b9", "Rs.")
    print(f"   Snippet: {text}...")
