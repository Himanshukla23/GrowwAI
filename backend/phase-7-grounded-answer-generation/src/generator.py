"""
Phase 4.5: Grounded Answer Generation Layer

Adheres to rag-architecture.md Section 4.5:
- Uses Groq API (groq) to answer user questions based purely on retrieved context.
- Implements strict prompt constraints (3 sentences max, neutral tone, citation format).
- Follows the "No evidence, no answer" hallucination prevention rule.
"""
import os
import pathlib
import sys
from groq import Groq
from dotenv import load_dotenv

# Load Environment
ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

class AnswerGenerator:
    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
            print(f"[Generator] Initialized with model {GROQ_MODEL}")
        else:
            print("[Generator] WARNING: GROQ_API_KEY is missing. Answer generation will be disabled.")

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates a grounded answer based entirely on the provided context evidence.
        """
        # Hallucination prevention rule
        if not context or "No relevant mutual fund evidence" in context:
            return "I cannot answer this question because I could not find relevant factual evidence in my Groww Assist corpus."

        system_instruction = """You are 'Groww Assist AI', a premium, highly factual, neutral financial assistant.
You must follow the "Prompt Contract":
1. Answer the user's question USING ONLY the provided [Evidence] blocks.
2. The provided evidence is scraped from websites and tabular data may be flattened. If you see a sequence like "SBI Contra Direct Plan-Growth Equity Very High 408.34 0.75 4.3%", it represents [Fund Scheme Name] [Category] [Risk] [NAV] [Expense Ratio] [1Y Returns]. 
3. Based on the rule above, you CAN and MUST extract the expense ratio or NAV if it appears in the sequence. For example if someone asks for Expense Ratio of SBI Contra and the sequence has "0.75", you answer "The expense ratio is 0.75%".
4. If the evidence absolutely does NOT contain any data related to the answer, reply exactly with: "I cannot answer this question based on the official Groww Assist corpus." Do not hallucinate.
5. Your answer must be a MAXIMUM of 3 sentences.
6. Maintain a strictly objective, neutral tone.

Your response MUST be a clear, direct answer:
- Sentence 1: The direct factual answer with exact values.
- Sentence 2: Any qualifying condition or context.
- Sentence 3: (Optional) A brief process step.

DO NOT include any 'Source:' links or 'Last updated' footers in your response text."""

        prompt = f"""User Query: "{query}"

=== EVIDENCE CONTEXT ===
{context}
========================

Please generate the answer strictly following the template and contract rules."""

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0 # Zero temperature for strict factual groundedness
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[Generator] Error during generation: {e}")
            return "An internal generation error occurred."

    def extract_fund_data(self, evidence: str, intent: str = "factual") -> dict:
        """
        Extract structured fund metrics from the evidence context.
        Returns a dictionary compatible with the frontend's Workspace props.
        """
        if not evidence or "No relevant mutual fund evidence" in evidence:
            return None

        import json
        
        if intent == "comparison":
            system_instruction = """You are a precise data extraction engine for mutual fund comparisons. 
Extract details for TWO funds being compared from the evidence. 
Return ONLY a JSON object with these keys: 
- fundA: { name, type, nav, change, logo (null) }
- fundB: { name, type, nav, change, logo (null) }
- metrics: array of { label, a, b, isBadge (boolean) }

Include metrics like 'Expense Ratio', 'Risk Category', 'Min. Investment', 'Returns'.
If a value is not found, use null.
Return ONLY valid JSON."""
        else:
            system_instruction = """You are a precise data extraction engine. 
Extract the primary mutual fund's details from the provided evidence. 
Return ONLY a JSON object with these keys: 
- name (string, full fund name)
- type (string, e.g. Equity, Debt, Commodity)
- plan (string, e.g. Direct Plan • Growth)
- nav (string, just the number, e.g. "54.20")
- navDate (string, e.g. "14 May 2024")
- change (string, include sign, e.g. "+1.2%" or "-0.5%")
- risk (string, e.g. "Very High Risk", "High Risk", "Moderate Risk", "Low Risk")
- expenseRatio (string, e.g. "0.64%")
- exitLoad (string, e.g. "1%")
- aum (string, e.g. "₹4,210 Cr")
- category (string, e.g. "Commodities", "Mid Cap", "Large Cap")
- alphaScore (string, a score from 1-10 based on returns quality; estimate if not explicit)
- holdings (array of up to 5 objects, each with 'name' (sector or stock name) and 'value' (percentage as string e.g. "35%"). Extract from any portfolio allocation, sector breakdown, or top holdings data in the evidence. If no holdings data exists, return an empty array [].)

If a value is not found in the evidence, use null.
Return ONLY valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Extract data from this evidence:\n\n{evidence}"}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content.strip())
            return data
        except Exception as e:
            print(f"[Generator] Extraction error: {e}")
            return None

if __name__ == "__main__":
    # Import the pipeline to test full end-to-end flow
    sys.path.append(str(ROOT / "backend" / "phase-6-retrieval-reranking-layer" / "src"))
    from pipeline import RetrievalPipeline
    from retriever import Retriever
    
    print("\n[E2E Test] Initializing ChromaDB and Groq...")
    db_retriever = Retriever()
    search_pipeline = RetrievalPipeline(db_retriever)
    generator = AnswerGenerator()
    
    query = "what is the expense ratio of SBI Contra Fund Direct Growth"
    print(f"\nUser Query: '{query}'")
    
    # 1. Run Retrieval Pipeline
    print("\n--- 1. Semantic Retrieval ---")
    pipeline_result = search_pipeline.run(query=query)
    
    if pipeline_result.get("error"):
        print(f"Pipeline Guardrail Blocked: {pipeline_result.get('error')}")
        sys.exit(0)
        
    context_str = pipeline_result.get("evidence_context", "")
    print(f"Retrieved Context Length: {len(context_str)} characters from {pipeline_result.get('chunks_used')} chunks.")
    
    # 2. Run Generation
    print("\n--- 2. Groq Grounded Generation ---")
    answer = generator.generate_answer(query, context_str)
    # Print safely to avoid Windows cp1252 encoding crashes on the Rupee symbol (₹)
    safe_answer = answer.replace('₹', 'Rs. ')
    print("\n" + safe_answer + "\n")
