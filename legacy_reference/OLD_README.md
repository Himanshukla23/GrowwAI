# 🍽️ THE CURATOR | AI-Powered Restaurant Discovery

A premium, end-to-end restaurant recommendation platform that uses **Llama 3.1 8B (via Groq)** and **Weighted TF-IDF Ranking** to deliver context-aware dining suggestions.

---

## 🚀 Experience the Platform

| **Component** | **Description** | **How to Run** |
| :--- | :--- | :--- |
| **Premium Frontend** | Next.js Powered Dark-Mode UI | `cd frontend && npm run dev` |
| **Admin Dashboard** | Streamlit Testing & Stats UI | `streamlit run streamlit_app.py` |
| **API Backend** | FastAPI Powered Scoring Engine | `uvicorn app.main:app --reload` |
| **Data Ingestion** | Hugging Face Dataset Sync | `python scripts/init_data.py` |

---

## 🏗️ Architecture Stack

- **Llama 3.1 8B (Groq)**: High-speed LLM for ranking and explaining recommendations.
- **FastAPI**: Non-blocking asynchronous API backend.
- **SQLite**: Reliable, persistent local data storage.
- **Next.js & Streamlit**: Dual-platform UI for users and developers.
- **TF-IDF & Cosine Similarity**: Mathematical relevance scoring for candidate selection.

---

## 📂 Project Navigation

- **📁 [/app](file:///app)**: FastAPI application entry points and model schemas.
- **📁 [/frontend](file:///frontend)**: Next.js source code (Premium User Interface).
- **📁 [/src](file:///src)**: Core logic, split into development phases (Phases 1-4).
- **📁 [/data](file:///data)**: Persistent SQLite database and request logs.
- **📁 [/scripts](file:///scripts)**: Database initialization and testing scripts.
- **📁 [/docs](file:///docs)**: Original [Architecture-Plan.md](file:///docs/Architecture-Plan.md) and design specifications.
- **📄 [streamlit_app.py](file:///streamlit_app.py)**: The Streamlit dashboard entry point.

---

## 🔧 Installation & Setup

1.  **Clone and Install**:
    ```bash
    git clone https://github.com/Himanshukla23/Zomato-AI.git
    cd Zomato-AI
    pip install -r requirements.txt
    ```
2.  **Set Environment Variables**:
    Create a `.env` file with:
    ```env
    GROQ_API_KEY=your_key_here
    API_AUTH_TOKEN=your_token_here
    ```
3.  **Initialize Database**:
    ```bash
    python scripts/init_data.py
    ```
4.  **Run!**:
    Choose your platform (FastAPI, Next.js, or Streamlit) and follow the table above.

---

## 🤝 Project Credits
Created as a professional-grade AI solution for the Zomato dataset exploration. 

**Powered by Groq • Llama 3.1 • Next.js • Streamlit**
