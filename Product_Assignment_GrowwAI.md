# Product Assignment: Improving an Everyday Product
**Target App:** Groww (Mutual Fund Segment)
**Proposed Solution:** Groww Assist AI (RAG-Powered Financial Guide)

---

## 1. User & Problem
### Who is the user?
*   **The "Newbie" Investor:** Individuals starting their journey who feel overwhelmed by the 100+ pages of scheme information.
*   **The "Data-Driven" Professional:** Investors who need specific facts (NAV, Exit Load, Expense Ratio) quickly without navigating multiple UI layers.

### What problem are they facing?
**Information Friction & Decision Paralysis.** Financial apps currently present data in a static way. A user has to manually search across multiple tabs, download PDFs, and perform their own comparisons. There is no "Assistant" that can fetch a specific fact instantly.

### User Stories
*   **Story 1:** As a new investor, I want to compare the risk and returns of two funds side-by-side, so I can choose the one that fits my risk appetite.
*   **Story 2:** As a busy professional, I want to instantly ask for a fund's exit load, so I can plan my withdrawals without Surprise charges.
*   **Story 3:** As a cautious user, I want to verify the AI's answer against official documents, so I can trust the data I see.

---

## 2. Solution
### What are you building?
**Groww Assist AI:** A context-aware, RAG-powered (Retrieval-Augmented Generation) financial assistant. It is a dual-pane interface: one side for chat and one side for a dynamic data dashboard.

### How does it improve the experience?
*   **Instant Grounded Answers:** Uses Semantic Search to find exact data in thousands of documents.
*   **Interactive Workspace:** The UI updates based on conversation. If you ask about a fund, the dashboard automatically loads that fund's chart.
*   **High Trust:** Built with a "Prompt Contract" that prevents the AI from guessing or giving biased advice.

---

## 3. User Flow
1.  **Entry:** User opens the "AI History" or clicks the "New Analysis" button.
2.  **Input:** User asks: *"Compare SBI Contra Fund and Nippon India Large Cap."*
3.  **Processing:** System retrieves relevant data chunks from **ChromaDB Cloud** using vector embeddings.
4.  **UI Update:** The dashboard pane switches to a **Comparison Grid** showing Expense Ratios, Risk, and NAV.
5.  **Verification:** User sees the generated answer and can click the **Source** link to view the original data.

---

## 4. Use Cases
1.  **Comparison:** Comparing 2-3 funds side-by-side based on live market data.
2.  **NAV Lookup:** Fetching the latest Net Asset Value without digging through menu layers.
3.  **Risk Analysis:** Summarizing complex risk factors into 3 simple sentences.
4.  **Technical Definitions:** Explaining terms like "Tracking Error" or "Standard Deviation" using live examples.
5.  **Operational Check:** Verifying exit loads and lock-in periods for ELSS funds.
6.  **Fact-Checking:** Proving an AI response using direct links to Groww's official scheme pages.

---

## 5. Edge Cases / Failure Scenarios
1.  **PII Detection:** User enters sensitive data (PAN, Aadhaar).
    *   *System Action:* Guardrails detect patterns and refuse to process the message.
2.  **Advisory Avoidance:** User asks "Should I buy this fund?"
    *   *System Action:* System identifies "Prohibited Intent" and provides a neutral, factual refusal.
3.  **Out-of-Scope Query:** User asks about the weather or recipes.
    *   *System Action:* System uses a fallback message to keep focus on mutual funds.
4.  **Empty Data:** User asks about a fund not in the current database.
    *   *System Action:* System provides a "Low Confidence" message and suggests checking the official page.
5.  **Multi-Fund Ambiguity:** User mentions two funds but asks "What is its return?"
    *   *System Action:* System asks the user to clarify which of the two funds they mean.

---

## 6. Success Metrics
*   **Time to Data (TTD):** Average time taken for a user to find a specific fact (Target: < 3 seconds).
*   **Query Resolution Rate:** Percentage of queries that result in a factual answer vs. a fallback.
*   **Workspace Activation:** How many times the dashboard automatically updates based on AI intent detection.
*   **NPS/CSAT:** User satisfaction regarding the "Helpfulness" and "Trustworthiness" of the AI.

---
**Live Prototype:** [https://groww-ai.vercel.app/](https://groww-ai.vercel.app/)
