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
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MODELS_TO_TRY = list(dict.fromkeys([GROQ_MODEL, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]))

class AnswerGenerator:
    def __init__(self):
        self.client = None
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
            print(f"[Generator] Initialized with primary model {GROQ_MODEL}")
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
2. If the user asks to compare schemes (e.g. "Compare X and Y"):
   - Directly contrast the key metrics from the evidence (NAV, Expense Ratio, 3Y returns, Category, Risk, Minimum SIP) for both funds in 2-3 objective sentences.
   - Example format: "SBI Contra Direct Plan has an NAV of ₹411.80, an expense ratio of 0.75%, and 3-year returns of 62.25%, whereas Nippon India Large Cap Fund has an NAV of ₹100.79, an expense ratio of 0.71%, and 3-year returns of 62.66%. Nippon India Large Cap offers a slightly lower expense ratio and minimum SIP (₹100 vs ₹500), while SBI Contra focuses on value-oriented equity."
3. For factual metric questions (e.g. "What is the ER of X?"):
   - Sentence 1: The direct factual answer with exact values.
   - Sentence 2: Any qualifying condition, category, or date.
4. If the evidence absolutely does NOT contain any data related to the schemes or query, reply exactly with: "I cannot answer this question based on the official Groww Assist corpus." Do not hallucinate.
5. Keep your response within 3 sentences maximum. Maintain a strictly objective, neutral tone.
6. DO NOT include any 'Source:' links or 'Last updated' footers in your response text."""

        prompt = f"""User Query: "{query}"

=== EVIDENCE CONTEXT ===
{context}
========================

Please generate the answer strictly following the template and contract rules."""

        for model_name in MODELS_TO_TRY:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Generator] Error with model {model_name}: {e}")
                continue

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
Return ONLY a JSON object with this exact structure: 
{
  "funds": [
    {
      "name": "Full scheme name (e.g. SBI Contra Fund Direct Growth)",
      "type": "Category type (e.g. Equity, Debt, Gold Fund, Mid Cap)",
      "nav": "NAV number only (e.g. 408.34)",
      "change": "Percentage change with sign (e.g. +4.3% or -1.2%)",
      "expenseRatio": "Expense ratio percentage (e.g. 0.75%)",
      "risk": "Risk level (e.g. Very High, High, Moderate, Low)",
      "minInvestment": "Minimum investment (e.g. ₹500 or ₹5,000)",
      "returns3Y": "3-year returns percentage (e.g. 24.5%)",
      "desc": "1-sentence summary of the scheme objective"
    },
    {
      "name": "Second scheme name",
      "type": "Category type",
      "nav": "NAV number only",
      "change": "Percentage change with sign",
      "expenseRatio": "Expense ratio percentage",
      "risk": "Risk level",
      "minInvestment": "Minimum investment",
      "returns3Y": "3-year returns percentage",
      "desc": "1-sentence summary of the scheme objective"
    }
  ],
  "insight": "A concise 2-sentence comparative takeaway contrasting the risk and return profiles of these two funds."
}

If any value is not found in the evidence, use null.
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

        for model_name in MODELS_TO_TRY:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Extract data from this evidence:\n\n{evidence}"}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                raw_text = response.choices[0].message.content.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                data = json.loads(raw_text)
                if intent == "comparison" and isinstance(data, dict):
                    if "funds" in data and isinstance(data["funds"], list):
                        if len(data["funds"]) > 0 and "fundA" not in data:
                            data["fundA"] = data["funds"][0]
                        if len(data["funds"]) > 1 and "fundB" not in data:
                            data["fundB"] = data["funds"][1]
                    elif "fundA" in data and "fundB" in data:
                        data["funds"] = [data["fundA"], data["fundB"]]
                return data
            except Exception as e:
                print(f"[Generator] Extraction error with {model_name}: {e}")
                continue
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
