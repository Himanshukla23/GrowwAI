# Phase 1: Scheduler Service

## Responsibilities
- Run a scheduled refresh job **daily at 09:15 IST** (03:45 UTC).
- Trigger the data ingestion pipeline (Scraping -> Processing -> Indexing).
- Maintain run logs in `data/scheduler-runs`.

## Components
- `src/scheduler.py`: Main orchestration script.
- `.github/workflows/daily-rag-refresh.yml`: Cron-based workflow trigger.
