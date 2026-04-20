import sys
import pathlib
import os

# 1. Resolve Pathing
ROOT = pathlib.Path(__file__).resolve().parent
print(f"[Main] Root directory: {ROOT}")

# 2. Add phase directories to path
# We use absolute paths to ensure Render's environment finds them
phase_6 = ROOT / "backend" / "phase-6-retrieval-reranking-layer" / "src"
phase_7 = ROOT / "backend" / "phase-7-grounded-answer-generation" / "src"
phase_8 = ROOT / "backend" / "phase-8-policy-safety-guardrails" / "src"
phase_9 = ROOT / "backend" / "phase-9-api-multi-thread-chat" / "src"

for p in [phase_6, phase_7, phase_8, phase_9]:
    if p.exists():
        sys.path.insert(0, str(p))
        print(f"[Main] Path Added: {p}")
    else:
        print(f"[Main] WARNING: Path not found: {p}")

# 3. Create FastAPI Instance
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Groww Assist AI — Final Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Attempt to import the real logic
try:
    # We import the routes/logic from app.py but we define our own app instance here for stability
    import app as backend_logic
    # Re-mount/Import routes if they exist in a router, or just use the backend_logic.app
    # To keep it simple and stable, we'll proxy to the real app
    from app import app as real_app
    app = real_app
    print("[Main] Successfully connected and loaded Phase 9 Logic")
except Exception as e:
    print(f"[Main] CRITICAL ERROR during logic load: {e}")
    # Minimal routes so the server stays UP for debugging
    @app.get("/")
    def fail_root():
        return {"status": "error", "message": "Failed to load backend logic. Check Render Logs.", "error": str(e)}

    @app.get("/health")
    def fail_health():
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
