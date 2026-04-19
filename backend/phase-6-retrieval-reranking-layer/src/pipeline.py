"""
Phase 6: Retrieval and Re-ranking Layer (Full Pipeline)

This module builds on top of `retriever.py` to add:
1. Intent Classification (via Groq)
2. Query Rewriting (via Groq)
3. Re-ranking
4. Evidence Packing
"""
import os
import pathlib
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, List

# Load Environment
ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

class RetrievalPipeline:
    def __init__(self, retriever_instance):
        self.retriever = retriever_instance
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        
        if not self.client:
            print("[Warning] GROQ_API_KEY is not set. Intent Classification and Query Rewriting will use basic fallback heuristics.")

    def classify_intent(self, query: str) -> str:
        """
        Classify intent into: 'factual', 'advisory', 'comparison', or 'out-of-scope'.
        Uses Groq LLM if available, otherwise falls back to basic keyword rules.
        """
        # 1. Basic Rule-Based Fallback
        lower_q = query.lower()
        advisory_keywords = ["should i", "invest in", "is it good", "recommend", "best fund"]
        comparison_keywords = ["compare", "vs", "versus", "difference between"]
        
        if any(kw in lower_q for kw in advisory_keywords):
            return "advisory"
        if any(kw in lower_q for kw in comparison_keywords):
            return "comparison"
            
        if not self.client:
            return "factual" # Default fallback
            
        # 2. LLM-Based Classification
        try:
            prompt = f"""Classify the intent of this user query for a Mutual Fund AI assistant.
Options: 'factual', 'advisory', 'comparison', 'out-of-scope'.
'comparison' is for queries asking to compare two or more funds.
Query: "{query}"
Reply exactly with one of the options, nothing else."""

            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            intent = response.choices[0].message.content.strip().lower()
            if intent in ['factual', 'advisory', 'comparison', 'out-of-scope']:
                return intent
            return "factual"
        except Exception as e:
            print(f"[Pipeline] LLM Intent Classification failed: {e}")
            return "factual"


    def rewrite_query(self, query: str) -> str:
        """Expand acronyms, fix typos, and clarify query context for RAG."""
        if not self.client:
            # Simple rule-based expansion
            expanded = query.lower().replace(" er ", " expense ratio ").replace(" nav ", " net asset value ").replace(" sip ", " systematic investment plan ")
            expanded = expanded.replace("sbi", "SBI Mutual Fund schemes").replace("hdfc", "HDFC Mutual Fund schemes")
            return expanded
            
        try:
            prompt = f"""You are a query expansion engine for a Mutual Fund RAG system.
Rewrite this user query to:
1. Fix any typos (e.g., 'Comapre' -> 'Compare', 'SPI' -> 'SIP').
2. Expand acronyms: ER -> Expense Ratio, NAV -> Net Asset Value, MF -> Mutual Fund.
3. Clarify truncated AMC names: 'SBI' -> 'SBI Mutual Fund', 'HDFC' -> 'HDFC Mutual Fund'.
4. If the user mentions only an AMC (like 'HDFC' or 'SBI') without a specific fund, expand the query to include terms like "top schemes", "minimum investment", and "SIP amount" to ensure the search retrieves relevant data from individual fund pages.

User Query: "{query}"

Reply ONLY with the rewritten query string. No explanations."""
            
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Pipeline] LLM Query Rewriting failed: {e}")
            return query

    def rerank(self, query: str, raw_results: List[Dict]) -> List[Dict]:
        """
        Re-ranks the raw semantic results.
        Uses a lightweight heuristic: boosting documents where exact query terms appear in the scheme name or source url.
        """
        if not raw_results:
            return []
            
        query_terms = set(query.lower().split())
        for res in raw_results:
            # Base score inversely proportional to distance (lower distance = better)
            score = 1.0 / (1.0 + res['distance'])
            
            # Boost if scheme name closely matches
            scheme_name = res['metadata'].get('scheme_name', '').lower()
            if any(term in scheme_name for term in query_terms if len(term) > 3):
                score += 0.2
                
            res['rerank_score'] = score
            
        # Sort by the new score descending
        reranked = sorted(raw_results, key=lambda x: x['rerank_score'], reverse=True)
        return reranked

    def pack_evidence(self, reranked_chunks: List[Dict], max_chunks: int = 3) -> str:
        """Formats the top N chunks into an injected context string."""
        evidence = []
        for i, chunk in enumerate(reranked_chunks[:max_chunks]):
            source = chunk['metadata'].get('source_url', 'Unknown URL')
            amc = chunk['metadata'].get('amc_name', 'Unknown AMC')
            # Clean newlines for cleaner prompt injection
            text = chunk['text'].replace('\n', ' ').strip()
            
            block = f"[Evidence {i+1} | Source: {amc} | URL: {source}]\n{text}"
            evidence.append(block)
            
        if not evidence:
            return "No relevant mutual fund evidence found in the database."
            
        return "\n\n".join(evidence)

    def run(self, query: str, filters: dict = None, top_k: int = 15) -> Dict:
        """Executes the full Retrieval & Re-ranking pipeline."""
        print(f"\n[Pipeline] Starting pipeline for query: '{query}'")
        
        # 1. Intent Classification
        intent = self.classify_intent(query)
        print(f"[Pipeline] > Intent classified as: {intent}")
        
        if intent == "advisory":
            return {
                "error": "Groww Assist Policy: I cannot provide investment advice or recommendations. Please consult a registered SEBI financial advisor for personalized guidance.", 
                "intent": intent
            }
        if intent == "out-of-scope":
            return {
                "error": "Out of scope: This query does not appear to be related to mutual funds or Groww Assist datasets.", 
                "intent": intent
            }
            
        # 2. Query Rewriting
        rewritten_query = self.rewrite_query(query)
        if rewritten_query != query:
            print(f"[Pipeline] > Query rewritten to: '{rewritten_query}'")
        
        # 3. Retrieval
        print(f"[Pipeline] > Running ChromaDB retrieval (top_k={top_k})...")
        raw_results = self.retriever.retrieve(query=rewritten_query, top_k=top_k, filters=filters)
        
        # 4. Re-ranking
        print(f"[Pipeline] > Re-ranking {len(raw_results)} vectors...")
        reranked_results = self.rerank(rewritten_query, raw_results)
        
        # 5. Evidence Packing
        context_string = self.pack_evidence(reranked_results, max_chunks=5)
        print(f"[Pipeline] > Pipeline complete. Packed evidence string length: {len(context_string)} chars.")
        
        return {
            "intent": intent,
            "original_query": query,
            "rewritten_query": rewritten_query,
            "evidence_context": context_string,
            "chunks_used": len(reranked_results),
            "raw_results": reranked_results
        }


if __name__ == "__main__":
    from retriever import Retriever
    
    db_retriever = Retriever()
    pipeline = RetrievalPipeline(db_retriever)
    
    factual_query = "What is the ER of SBI Contra fund?"
    result = pipeline.run(query=factual_query)
    
    print("\n================== PIPELINE OUTPUT ==================")
    print(f"Original Query: {result.get('original_query')}")
    print(f"Rewritten:      {result.get('rewritten_query')}")
    print(f"Intent:         {result.get('intent')}")
    print("\n--- Packed Evidence for LLM ---")
    safe_evidence = result.get('evidence_context', '').replace('₹', 'Rs. ')
    print(safe_evidence)
    print("=====================================================")
    
    advisory_query = "Should I invest in SBI mutual funds?"
    adv_result = pipeline.run(query=advisory_query)
    print(f"\n[Guardrail Test]: {adv_result.get('error')}")
