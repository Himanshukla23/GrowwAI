import sys
import pathlib
import uvicorn

# Resolve root path
ROOT = pathlib.Path(__file__).resolve().parent

# Add all phase directories to sys.path to handle hyphenated names correctly
phases = [
    "phase-6-retrieval-reranking-layer",
    "phase-7-grounded-answer-generation",
    "phase-8-policy-safety-guardrails",
    "phase-9-api-multi-thread-chat"
]

for phase in phases:
    src_path = ROOT / "backend" / phase / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        print(f"[Main] Added to path: {src_path}")

# Now import the app from the phase-9 src directory
try:
    from app import app
    print("[Main] Successfully loaded Groww Assist API")
except ImportError as e:
    print(f"[Main] Critical Import Error: {e}")
    # Fallback to a dummy app so the server at least starts and we can see logs
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def error():
        return {"error": "Failed to load main application. Check logs.", "details": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
