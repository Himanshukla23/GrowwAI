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
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MODELS_TO_TRY = list(dict.fromkeys([GROQ_MODEL, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]))

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
        prompt = f"""Classify the intent of this user query for a Mutual Fund AI assistant.
Options: 'factual', 'advisory', 'comparison', 'out-of-scope'.
'comparison' is for queries asking to compare two or more funds.
Query: "{query}"
Reply exactly with one of the options, nothing else."""

        for model_name in MODELS_TO_TRY:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                intent = response.choices[0].message.content.strip().lower()
                if intent in ['factual', 'advisory', 'comparison', 'out-of-scope']:
                    return intent
                return "factual"
            except Exception as e:
                print(f"[Pipeline] LLM Intent Classification failed with {model_name}: {e}")
                continue

        return "factual"


    def rewrite_query(self, query: str) -> str:
        """Expand acronyms, fix typos, and clarify query context for RAG."""
        if not self.client:
            # Simple rule-based expansion
            expanded = query.lower().replace(" er ", " expense ratio ").replace(" nav ", " net asset value ").replace(" sip ", " systematic investment plan ")
            expanded = expanded.replace("sbi", "SBI Mutual Fund schemes").replace("hdfc", "HDFC Mutual Fund schemes")
            return expanded
            
        prompt = f"""You are a query expansion engine for a Mutual Fund RAG system.
Rewrite this user query to:
1. Fix any typos (e.g., 'Comapre' -> 'Compare', 'SPI' -> 'SIP').
2. Expand acronyms: ER -> Expense Ratio, NAV -> Net Asset Value, MF -> Mutual Fund.
3. Clarify truncated AMC names: 'SBI' -> 'SBI Mutual Fund', 'HDFC' -> 'HDFC Mutual Fund'.
4. If the user mentions only an AMC (like 'HDFC' or 'SBI') without a specific fund, expand the query to include terms like "top schemes", "minimum investment", and "SIP amount" to ensure the search retrieves relevant data from individual fund pages.

User Query: "{query}"

Reply ONLY with the rewritten query string. No explanations."""
        
        for model_name in MODELS_TO_TRY:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Pipeline] LLM Query Rewriting failed with {model_name}: {e}")
                continue

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

    def pack_evidence(self, reranked_chunks: List[Dict], max_chunks: int = 8, is_comparison: bool = False, query: str = "") -> str:
        """Formats the top N chunks into an injected context string, balancing schemes and prioritizing query matches."""
        if not reranked_chunks:
            return "No relevant mutual fund evidence found in the database."

        if is_comparison:
            by_scheme: Dict[str, List[Dict]] = {}
            for chunk in reranked_chunks:
                scheme = chunk.get('metadata', {}).get('scheme_name') or chunk.get('metadata', {}).get('source_url') or 'other'
                by_scheme.setdefault(scheme, []).append(chunk)

            # Sort chunks within each scheme so OFFICIAL SCHEME FACTS comes first
            for scheme in by_scheme:
                by_scheme[scheme].sort(
                    key=lambda c: (
                        0 if "OFFICIAL SCHEME FACTS" in c.get('text', '') else 1
                    )
                )

            # Score each scheme by relevance to query terms, excluding generic filler words
            q_lower = query.lower()
            generic_stopwords = {"fund", "funds", "mutual", "india", "direct", "growth", "plan", "the", "and", "scheme", "schemes", "compare", "between", "versus", "with"}
            q_words = set(q_lower.replace(",", " ").replace("vs", " ").split()) - generic_stopwords

            def scheme_relevance(s_name: str) -> int:
                s_lower = s_name.lower()
                score = 0
                for w in q_words:
                    if len(w) >= 3 and w in s_lower:
                        score += 3 if w in ["contra", "gold", "psu", "large", "mid", "small", "multi", "flexi", "focused"] else 1
                return score

            # Check if query mentions two distinct AMCs
            amcs_in_query = [amc for amc in ["sbi", "hdfc", "icici", "nippon"] if amc in q_lower]
            primary_schemes = []
            if len(amcs_in_query) >= 2:
                for amc in amcs_in_query[:2]:
                    matching_for_amc = [
                        s for s in by_scheme.keys()
                        if amc in s.lower() or any(amc in (c.get('metadata', {}).get('amc_name', '').lower()) for c in by_scheme[s])
                    ]
                    if matching_for_amc:
                        best = max(matching_for_amc, key=scheme_relevance)
                        primary_schemes.append(best)

            # Fallback if fewer than 2 schemes picked
            sorted_schemes = sorted(by_scheme.keys(), key=scheme_relevance, reverse=True)
            for s in sorted_schemes:
                if s not in primary_schemes:
                    primary_schemes.append(s)
                if len(primary_schemes) >= 2:
                    break

            # Guarantee that OFFICIAL SCHEME FACTS chunk is present for each primary scheme
            for scheme in primary_schemes:
                has_facts = any("OFFICIAL SCHEME FACTS" in c.get('text', '') for c in by_scheme.get(scheme, []))
                if not has_facts and self.retriever and getattr(self.retriever, 'collection', None):
                    try:
                        fact_res = self.retriever.collection.get(
                            where={"$and": [{"scheme_name": {"$eq": scheme}}, {"chunk_index": {"$eq": 0}}]}
                        )
                        if fact_res and fact_res.get('documents'):
                            fact_chunk = {
                                "chunk_id": fact_res['ids'][0],
                                "text": fact_res['documents'][0],
                                "metadata": fact_res['metadatas'][0],
                                "score": 1.0
                            }
                            by_scheme.setdefault(scheme, []).insert(0, fact_chunk)
                    except Exception as e:
                        print(f"[Pipeline] Fact lookup error for {scheme}: {e}")

            selected = []
            
            # First round: take top facts from the primary schemes
            for scheme in primary_schemes:
                if by_scheme[scheme]:
                    selected.append(by_scheme[scheme].pop(0))

            # Second round: take additional details for the primary schemes
            while len(selected) < max_chunks:
                added = False
                for scheme in primary_schemes:
                    if by_scheme[scheme] and len(selected) < max_chunks:
                        selected.append(by_scheme[scheme].pop(0))
                        added = True
                if not added:
                    # If primary exhausted, backfill from other schemes
                    for scheme in sorted_schemes[2:]:
                        if by_scheme[scheme] and len(selected) < max_chunks:
                            selected.append(by_scheme[scheme].pop(0))
                            added = True
                    if not added:
                        break
            chunks_to_pack = selected
        else:
            chunks_to_pack = reranked_chunks[:max_chunks]

        evidence = []
        for i, chunk in enumerate(chunks_to_pack):
            source = chunk.get('metadata', {}).get('source_url', 'Unknown URL')
            amc = chunk.get('metadata', {}).get('amc_name', 'Unknown AMC')
            scheme = chunk.get('metadata', {}).get('scheme_name', '')
            text = chunk.get('text', '').replace('\n', ' ').strip()
            
            scheme_header = f" | Scheme: {scheme}" if scheme else ""
            block = f"[Evidence {i+1} | Source: {amc}{scheme_header} | URL: {source}]\n{text}"
            evidence.append(block)
            
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
        context_string = self.pack_evidence(reranked_results, max_chunks=8, is_comparison=(intent == "comparison"), query=query)
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
