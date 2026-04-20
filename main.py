import os
import sys
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Setup Python Path immediately
ROOT = pathlib.Path(__file__).resolve().parent
phases = ["phase-6-retrieval-reranking-layer", "phase-7-grounded-answer-generation", "phase-8-policy-safety-guardrails", "phase-9-api-multi-thread-chat"]
for phase in phases:
    p = str(ROOT / "backend" / phase / "src")
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Define Stability Gateway
app = FastAPI(title="Groww Assist - Stability Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Groww Assist Backend Gateway is LIVE"}

# 3. Attempt to load real logic
try:
    from app import app as real_app
    app = real_app
    print("[Main] Successfully loaded Groww Assist Core Logic")
except Exception as e:
    print(f"[Main] Core Logic Load Failed: {e}")
    # Minimal health for debugging
    @app.get("/health")
    async def health():
        return {"status": "degraded", "error": str(e), "path": sys.path}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
