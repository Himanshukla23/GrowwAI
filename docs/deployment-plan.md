# Groww Assist — Deployment Plan

This plan outlines the steps to move the Groww Assist RAG application from local development to a production-ready environment.

## 🏗️ Architecture Overview
- **Frontend**: Next.js (Tailwind v4) deployed on **Vercel**.
- **Backend API**: FastAPI deployed on **Render**.
- **Scheduler (Data Refresh)**: Python script triggered via **GitHub Actions**.
- **Vector Database**: **ChromaDB Cloud** (Persistent managed storage).
- **LLM / Embeddings**: **Groq** (Generation) and **Sentence Transformers** (Embeddings).

---

## 🚀 Phase 1: Infrastructure Setup

### 1. Vector DB (ChromaDB Cloud)
Since Render/Vercel have ephemeral filesystems, you must use ChromaDB Cloud.
- Log in to [ChromaDB Cloud](https://www.trychroma.com/).
- Create a collection named `groww_mf_chunks`.
- Note down your `CHROMA_API_KEY`, `CHROMA_TENANT`, and `CHROMA_DATABASE`.

### 2. Environment Variables Secret Store
Ensure you have the following keys ready:
- `GROQ_API_KEY`: For Gemini/Llama via Groq.
- `CHROMA_API_KEY`: For vector storage.
- `BACKEND_URL`: URL of your Render service (used by Frontend).

---

## 🛠️ Phase 2: Backend Deployment (Render)

1. **GitHub Connection**: Connect your GrowwAI repository to [Render.com](https://render.com).
2. **Service Type**: Create a new **Web Service**.
3. **Configuration**:
   - **Runtime**: `Python 3.10+`
   - **Root Directory**: `backend/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn phase-9-api-multi-thread-chat.src.app:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   Add all keys from your `.env` file to the Render "Environment" tab.

---

## 🎨 Phase 3: Frontend Deployment (Vercel)

1. **GitHub Connection**: Import the repository into [Vercel](https://vercel.com).
2. **Configuration**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend/`
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`
3. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Set this to your Render service URL (e.g., `https://groww-assist-api.onrender.com`).

---

## 🕒 Phase 4: Scheduler Deployment (GitHub Actions)

The scheduler ensures the Groww corpus is refreshed daily.

1. **Workflow File**: Create `.github/workflows/daily-refresh.yml` in your repo:
```yaml
name: Daily Data Refresh
on:
  schedule:
    - cron: '15 3 * * *' # 09:15 IST (UTC+5:30)
  workflow_dispatch: # Allows manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run Ingestion
        env:
          CHROMA_API_KEY: ${{ secrets.CHROMA_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          # Add other necessary envs
        run: python backend/phase-1-scheduler-service/src/scheduler.py
```
2. **Repository Secrets**:
   Go to `Settings > Secrets and variables > Actions` in GitHub and add your `CHROMA_API_KEY` and `GROQ_API_KEY`.

---

## ✅ Phase 5: Verification & Testing

1. **Trigger Manual Refresh**: Go to GitHub Actions and run the "Daily Data Refresh" manually.
2. **Check Render Logs**: Ensure the API starts without errors and connects to ChromaDB Cloud.
3. **End-to-End Test**:
   - Open Vercel URL.
   - Ask: "What is the exit load of SBI Contra Fund?"
   - Verify the dashboard updates with the latest data and correct citations.

---

## 📈 Post-Deployment Maintenance
- **Monitoring**: Check Render's dashboard for latency spikes.
- **Freshness**: The footer in the dashboard should update its "Last Crawled" date daily after the GitHub Action completes.
