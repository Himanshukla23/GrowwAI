# Phase 3: Scaling

This module introduces production scaling mechanisms:
- **Containerization**: Dockerfile and docker-compose.yml available in the root.
- **Middleware**: Rate Limiting (in-memory) and API Key Authentication.
- **Reliability**: Async LLM calls with timeouts, retry logic, and exponential backoff.
- **Cost Control**: Token budget tracking to limit daily Groq API expenditure.
- **Storage**: SQLite for persistent records (replacing purely CSV caching logic, while remaining zero-config compared to Postgres).
- **Observability**: Structured JSON logging.

## Usage
All phase 3 routes are mounted under `/phase3`.

Configuration is managed via environment variables (see `src/phase3/config.py`).
