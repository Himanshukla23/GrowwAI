# Groww Assist — Developer Guide

This guide explains how to extend, modify, and maintain the Groww Assist platform.

---

## 🔍 How to Change Core Logic

### 1. Adding New Data Sources (Scraping)
To ingest data from a new Groww URL:
1.  **Register the URL**: Add it to `docs/rag-architecture.md` for tracking.
2.  **Run Scraper**: Use `backend/phase-2-scraping-service/src/scraper.py` (ensure it targets the new URL).
3.  **Index Data**: Run the ingestion pipeline to update ChromaDB in `/data/chroma`.

### 2. Tuning the AI Response (Generation)
The generation logic lives in `backend/phase-7-grounded-answer-generation/src/generator.py`.
-   **Change constraints**: Modify the `system_instruction` variable (e.g., change the sentence limit or tone).
-   **Modify template**: Update the template structure in `generate_answer`.

### 3. Restricting or Allowing Queries (Guardrails)
Safety logic is in `backend/phase-8-policy-safety-guardrails/src/guardrails.py`.
-   **Blocked Phrases**: Add keywords to `ADVISORY_PHRASES`.
-   **PII Detection**: Add new Regex patterns to `PII_PATTERNS`.
-   **Auto-Correction**: Update `post_generate` to handle new types of formatting violations.

### 4. Updating the Dashboard (Data Mapping)
If the backend extracts new fields, you must map them:
1.  **Backend**: Update `extract_fund_data` in `generator.py` to include the new JSON key.
2.  **Frontend**: Update `DashboardWorkspace.js` to receive and render the new prop.

---

## 🎨 How to Change UI/Styling

### 1. The Design System
We use **Tailwind v4** with a CSS-centric theme definition.
-   **Modify Colors/Fonts**: Edit the `@theme` block in `/frontend/app/globals.css`.
-   **Add New Components**: Place them in `/frontend/components` and use the Material 3 color tokens (e.g., `text-on-surface-variant`).

### 2. Chat Animations
Animations for the chat blocks are controlled using Tailwind classes and staggered `animationDelay`.
-   Edit `AssistantPanel.js` to change timing or effects.

---

## 📊 Observability & Debugging
-   **Log Files**: All requests are logged as JSONL in `data/logs/query_logs.jsonl`.
-   **Metrics**: Access `http://localhost:8000/metrics` to see the performance of the RAG pipeline.

---

## 📂 Common File Map

| Task | File |
| :--- | :--- |
| **API Endpoints** | `backend/phase-9-api-multi-thread-chat/src/app.py` |
| **Search Logic** | `backend/phase-6-retrieval-reranking-layer/src/retriever.py` |
| **Main Page UI** | `frontend/app/page.js` |
| **Global Styles** | `frontend/app/globals.css` |
| **API Config** | `frontend/lib/api-config.js` |
