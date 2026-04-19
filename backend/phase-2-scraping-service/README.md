# Phase 2: Scraping Service

## Responsibilities
- Fetch data from all configured corpus URLs.
- Extract relevant textual content from AMC and scheme pages.
- Clean and preprocess raw HTML content (removes boilerplate, scripts, styles).
- Prepare normalized text payloads for Phase 4 (Chunking).

## Components
- `src/scraper.py`: Main scraping logic using `urllib` and regex.
- Reads from `phase-3-source-intake-layer/config/source_registry.json`.
