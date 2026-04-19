import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from typing import Dict, List, Tuple


ROOT = pathlib.Path(__file__).resolve().parents[3]
# Now reading from Phase 3: Source Intake Layer
CONFIG_PATH = ROOT / "backend" / "phase-3-source-intake-layer" / "config" / "source_registry.json"
RAW_BASE = ROOT / "data" / "raw"
PROCESSED_BASE = ROOT / "data" / "processed" / "latest"


def _load_config() -> Dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _is_allowed_domain(url: str, allowed_domain: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc.endswith(allowed_domain)


def _fetch_url(url: str, timeout_sec: int = 30) -> Tuple[int, str]:
    req = urllib.request.Request(
        url=url,
        headers={
            "User-Agent": "GrowwAI-RAG-Scraper/1.0 (+https://github.com/actions)"
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        status = getattr(resp, "status", 200)
        body = resp.read().decode("utf-8", errors="ignore")
        return status, body


def _clean_html_to_text(html: str) -> str:
    # 1. Remove script and style blocks
    no_script = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    no_style = re.sub(r"<style.*?>.*?</style>", " ", no_script, flags=re.IGNORECASE | re.DOTALL)
    
    # 2. Add structural markers for block elements to preserve line breaks
    # This helps Phase 4 identify section boundaries
    blocks = ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br", "header", "footer", "section", "article"]
    for tag in blocks:
        html = re.sub(f"<{tag}[^>]*>", "\n", html, flags=re.IGNORECASE)
        html = re.sub(f"</{tag}>", "\n", html, flags=re.IGNORECASE)

    # 3. Strip remaining tags
    no_tags = re.sub(r"<[^>]+>", " ", html)
    
    # 4. Normalize whitespace but preserve single newlines
    unescaped = unescape(no_tags)
    # Collapse horizontal spaces but keep vertical spacing
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in unescaped.splitlines()]
    # Remove empty lines and join with single newline
    normalized = "\n".join([line for line in lines if line])
    
    return normalized


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _write_json(path: pathlib.Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def run_scrape(fail_on_errors: bool) -> int:
    cfg = _load_config()
    allowed_domain = cfg["allowed_domain"]
    urls: List[Dict] = cfg["urls"]

    now_utc = dt.datetime.now(dt.timezone.utc)
    run_id = now_utc.strftime("%Y%m%dT%H%M%SZ")
    raw_dir = RAW_BASE / run_id
    processed_docs = []
    summary_rows = []
    failures = 0

    for idx, row in enumerate(urls):
        url = row["url"]
        if not _is_allowed_domain(url, allowed_domain):
            failures += 1
            summary_rows.append(
                {
                    "index": idx,
                    "url": url,
                    "status": "rejected",
                    "reason": "domain_not_allowed",
                }
            )
            continue

        try:
            status_code, html = _fetch_url(url)
            text = _clean_html_to_text(html)
            fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()

            raw_payload = {
                "url": url,
                "status_code": status_code,
                "fetched_at": fetched_at,
                "html_length": len(html),
                "html": html,
            }
            _write_json(raw_dir / f"{idx:03d}.json", raw_payload)

            processed_doc = {
                "document_id": f"groww-{idx:03d}",
                "source": cfg["source"],
                "url": url,
                "domain": urllib.parse.urlparse(url).netloc,
                "amc_name": row.get("amc_name"),
                "scheme_name": row.get("scheme_name"),
                "document_type": row.get("document_type"),
                "fetched_at": fetched_at,
                "content_hash": _sha256(text),
                "clean_text": text,
                "pipeline_version": "phase-2-v1",
            }
            processed_docs.append(processed_doc)
            summary_rows.append(
                {
                    "index": idx,
                    "url": url,
                    "status": "ok",
                    "status_code": status_code,
                    "clean_text_length": len(text),
                }
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            failures += 1
            summary_rows.append(
                {
                    "index": idx,
                    "url": url,
                    "status": "failed",
                    "reason": str(exc),
                }
            )

    PROCESSED_BASE.mkdir(parents=True, exist_ok=True)
    _write_json(
        PROCESSED_BASE / "documents.json",
        {
            "run_id": run_id,
            "generated_at": now_utc.isoformat(),
            "total_configured_urls": len(urls),
            "successful_documents": len(processed_docs),
            "documents": processed_docs,
        },
    )
    _write_json(
        PROCESSED_BASE / "run-summary.json",
        {
            "run_id": run_id,
            "generated_at": now_utc.isoformat(),
            "total_configured_urls": len(urls),
            "successful": len(processed_docs),
            "failed": failures,
            "details": summary_rows,
        },
    )

    print(f"[scraper] run_id={run_id} configured={len(urls)} success={len(processed_docs)} failed={failures}")
    if failures and fail_on_errors:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2 scraping service for Groww corpus.")
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Exit with non-zero code if any URL scrape fails.",
    )
    args = parser.parse_args()
    code = run_scrape(fail_on_errors=args.fail_on_errors)
    sys.exit(code)


if __name__ == "__main__":
    main()
