import os
from dotenv import load_dotenv

load_dotenv()

class Phase3Settings:
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    
    # Auth
    API_AUTH_TOKEN: str = os.getenv("API_AUTH_TOKEN", "")  # If empty, auth is disabled for dev
    
    # LLM Reliability
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "15.0"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    
    # Cost Control / Token Budget
    TOKEN_BUDGET_PER_REQUEST: int = int(os.getenv("TOKEN_BUDGET_PER_REQUEST", "2000"))
    TOKEN_BUDGET_DAILY: int = int(os.getenv("TOKEN_BUDGET_DAILY", "100000"))
    
    # Database (SQLite)
    DB_PATH: str = os.getenv("DB_PATH", "data/phase3_restaurants.sqlite")
    
    # Observability
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Phase3Settings()
