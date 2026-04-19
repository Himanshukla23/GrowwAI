# Groww Assist — Intelligent Mutual Fund Analyst

Groww Assist is a premium, RAG-powered financial intelligence platform designed to provide factual, grounded insights into mutual fund schemes. It employs a multi-phase backend architecture and a high-performance Next.js frontend to deliver real-time data with strict safety guardrails.

---

## 🏗️ Project Structure

The project is structured into three main layers to ensure modularity and ease of maintenance:

### 1. [Frontend](./frontend) (Next.js 14)
*   **Location**: `/frontend`
*   **Tech**: React, Tailwind v4, Material 3 Tokens.
*   **Key Components**:
    *   `AssistantPanel.js`: AI Chat interface with figure highlighting and clickable source links.
    *   `DashboardWorkspace.js`: Interactive data visualization for fund metrics.
    *   `ComparisonWorkspace.js`: Side-by-side fund analysis.

### 2. [Backend](./backend) (FastAPI + ChromaDB)
*   **Location**: `/backend`
*   **Phased Architecture**: The backend is divided into 10 distinct "Phases" (from Scraper to API).
*   **Key Engines**:
    *   `Retriever`: ChromaDB-powered semantic search.
    *   `Generator`: Groq-powered grounded answer generation.
    *   `Guardrails`: Policy enforcement layer (Advisory, PII, Scope).

### 3. [Knowledge Base](./docs)
*   **Location**: `/docs`
*   **Architecture**: `rag-architecture.md`
*   **Corpus**: `suggested-questions.md`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key (in `.env`)

### Setup Backend
1. `pip install -r requirements.txt`
2. `cd backend/phase-9-api-multi-thread-chat/src`
3. `uvicorn app:app --reload`

### Setup Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---

## 🛠️ Maintenance & Changes

To keep the system "easy to change", follow these entry points:

- **Adding new Mutual Funds**: Update the URL list in `docs/rag-architecture.md` and run the scraper in `backend/phase-2-scraping-service`.
- **Modifying AI Persona/Tone**: Edit `backend/phase-7-grounded-answer-generation/src/generator.py`.
- **Updating Safety Rules**: Modify `backend/phase-8-policy-safety-guardrails/src/guardrails.py`.
- **Changing UI Theme**: Edit `frontend/app/globals.css` (Tailwind v4 theme block).

For more details, see the [**Developer Guide**](./DEVELOPER_GUIDE.md).
