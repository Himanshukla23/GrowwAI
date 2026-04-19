import sys
import pathlib
import os

# Set root to the workspace root
ROOT = pathlib.Path(r"c:\Users\himan\GrowwAI")
sys.path.append(str(ROOT / "backend" / "phase-6-retrieval-reranking-layer" / "src"))

from retriever import Retriever
from pipeline import RetrievalPipeline

def main():
    retriever = Retriever()
    pipeline = RetrievalPipeline(retriever)
    
    query = "What is the minimum lumpsum investment for HDFC Equity Fund?"
    print(f"\n[Test] Query: {query}")
    
    result = pipeline.run(query=query)
    
    print("\n--- INTENT ---")
    print(result.get('intent'))
    
    print("\n--- PACKED EVIDENCE ---")
    evidence = result.get('evidence_context', '').replace('₹', 'Rs. ')
    print(evidence)
    
    print("\n--- RAW RESULTS ---")
    for r in result.get('raw_results', [])[:3]:
        print(f"\nDistance: {r['distance']:.4f}")
        print(f"URL: {r['metadata'].get('source_url')}")
        text_preview = r['text'].replace('₹', 'Rs. ').replace('\n', ' ')
        print(f"Text Preview: {text_preview[:200]}...")

if __name__ == "__main__":
    main()
