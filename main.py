import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import pathlib

# Stability First: Create the app instance immediately
app = FastAPI(title="Groww Assist - Minimal Stability Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Groww Assist Backend is LIVE",
        "note": "If /health is 404, check the logs for import errors."
    }

@app.get("/health")
async def health():
    # Try to report on internal state
    try:
        import app as backend_core
        return {
            "status": "healthy",
            "internal_logic": "loaded",
            "python_path": sys.path
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "cwd": os.getcwd(),
            "path": sys.path
        }

# Inject paths after app creation to prevent blocking startup
ROOT = pathlib.Path(__file__).resolve().parent
for phase in ["phase-6-retrieval-reranking-layer", "phase-7-grounded-answer-generation", "phase-8-policy-safety-guardrails", "phase-9-api-multi-thread-chat"]:
    p = str(ROOT / "backend" / phase / "src")
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    # Attempt to bridge to the main router if it exists
    from app import app as real_app
    app.mount("/api", real_app)
    print("Successfully mounted real_app logic at /api")
except Exception as e:
    print(f"Logic Bridge Failed: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
