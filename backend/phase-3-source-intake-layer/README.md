# Phase 3: Source Intake Layer

## Responsibilities
- Accept only URLs from `groww.in/mutual-funds/*`.
- Maintain `source_registry.json` with metadata.
- Track crawl status, checksum/hash, and domain allowlist.

## Components
- `config/source_registry.json`: The central allowlist of Groww URLs and scheme metadata.
