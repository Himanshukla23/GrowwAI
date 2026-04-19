from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    DATA_CACHE_PATH: str = os.getenv("DATA_CACHE_PATH", "data/processed_restaurants.csv")
    LLM_CACHE_TTL_SECONDS: int = int(os.getenv("LLM_CACHE_TTL_SECONDS", "900"))
    LLM_CACHE_MAX_ITEMS: int = int(os.getenv("LLM_CACHE_MAX_ITEMS", "500"))


settings = Settings()
