from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from src.phase4.backend.api.routes import router as phase4_router
from src.phase3.api.routes import router as phase3_router
from src.phase3.middleware.rate_limiter import RateLimiterMiddleware
from src.phase3.middleware.auth import APIKeyAuthMiddleware
from scripts.init_data import main as init_db_logic
import os

app = FastAPI(title="Restaurant Recommendation MVP")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Ensure database is initialized on Render
    db_path = "data/phase3_restaurants.sqlite"
    if not os.path.exists(db_path):
        print("🚀 Initializing database for the first time...")
        try:
            init_db_logic()
            print("✅ Database initialized successfully.")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

app.include_router(router)
app.include_router(phase4_router)
app.include_router(phase3_router)

# Phase 3 Middlewares (added in reverse order of execution)
app.add_middleware(APIKeyAuthMiddleware)
app.add_middleware(RateLimiterMiddleware)
