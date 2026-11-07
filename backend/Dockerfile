# ── Ultra-Fast, Lean Production Image for Render ───────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Optimization flags: disable bytecode, disable pip cache, unbuffered logs
ENV PYTHONPATH=/app \
    PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FASTEMBED_CACHE_PATH=/app/data/fastembed_cache

# 1. Copy dependencies first to maximize Docker layer cache
COPY requirements.txt .

# 2. Install lean dependencies (all have binary wheels, no compiler needed)
RUN pip install -r requirements.txt

# 3. Pre-download FastEmbed model during build
# This completely eliminates the 40-60 second HuggingFace download during container boot!
RUN python -c "from fastembed import TextEmbedding; import pathlib; p = pathlib.Path('/app/data/fastembed_cache'); p.mkdir(parents=True, exist_ok=True); TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir=str(p))"

# 4. Copy backend source code (frequently changed files at the end)
COPY main.py .
COPY backend/ ./backend/

# 5. Start Uvicorn with 1 worker (optimal for Render 512MB RAM free tier)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
