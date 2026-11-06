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


def _extract_structured_facts(html: str) -> str:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
    if not m:
        return ""
    try:
        nd = json.loads(m.group(1))
        props = nd.get("props", {}).get("pageProps", {})
    except Exception:
        return ""

    facts = []
    # Mutual fund scheme page
    if "mfServerSideData" in props and isinstance(props["mfServerSideData"], dict):
        mf = props["mfServerSideData"]
        s_name = mf.get("scheme_name") or mf.get("fund_name") or ""
        fund_house = mf.get("fund_house") or mf.get("amc") or ""
        category = mf.get("category") or ""
        sub_cat = mf.get("sub_category") or ""
        bench = mf.get("benchmark_name") or mf.get("benchmark") or ""
        nav = mf.get("nav")
        nav_date = mf.get("nav_date") or ""
        er = mf.get("expense_ratio")
        aum = mf.get("aum")
        risk = mf.get("risk") or mf.get("nfo_risk") or ""
        min_sip = mf.get("min_sip_investment")
        min_lump = mf.get("min_investment_amount")
        exit_load = mf.get("exit_load") or ""
        fund_mgr = mf.get("fund_manager") or ""
        desc = mf.get("description") or ""

        sr = mf.get("simple_return") or {}
        r1y = sr.get("return1y")
        r3y = sr.get("return3y")
        r5y = sr.get("return5y")

        facts.extend([
            f"=== OFFICIAL SCHEME FACTS: {s_name} ===",
            f"Scheme Name: {s_name}",
            f"Fund House (AMC): {fund_house}",
            f"Category: {category} ({sub_cat})",
            f"Benchmark: {bench}",
            f"Latest Net Asset Value (NAV): ₹{nav:.4f}" if isinstance(nav, (int, float)) else f"Latest Net Asset Value (NAV): ₹{nav}",
            f"NAV Date: {nav_date}",
            f"Expense Ratio: {er}%" if er is not None else "Expense Ratio: N/A",
            f"AUM (Fund Size): ₹{aum:,.2f} Cr" if isinstance(aum, (int, float)) else f"AUM (Fund Size): ₹{aum} Cr",
            f"Risk Level: {risk}",
            f"Minimum SIP Investment: ₹{min_sip}" if min_sip is not None else "Minimum SIP Investment: N/A",
            f"Minimum Lumpsum Investment: ₹{min_lump}" if min_lump is not None else "Minimum Lumpsum Investment: N/A",
            f"1-Year Return: {r1y:.2f}%" if isinstance(r1y, (int, float)) else f"1-Year Return: {r1y}%",
            f"3-Year Return: {r3y:.2f}%" if isinstance(r3y, (int, float)) else f"3-Year Return: {r3y}%",
            f"5-Year Return: {r5y:.2f}%" if isinstance(r5y, (int, float)) else f"5-Year Return: {r5y}%",
            f"Exit Load: {exit_load}",
            f"Fund Manager: {fund_mgr}",
            f"Investment Objective: {desc}",
            "=== END OF SCHEME FACTS ==="
        ])

    # AMC main page
    if "amcMainPageData" in props and isinstance(props["amcMainPageData"], list):
        amc_list = props["amcMainPageData"]
        if len(amc_list) > 1 and isinstance(amc_list[1], dict) and "key_information" in amc_list[1]:
            kinfo = amc_list[1]["key_information"] or {}
            fhouse = kinfo.get("fund_house") or kinfo.get("asset_management_company") or ""
            tot_aum = kinfo.get("total_aum")
            sponsors = ", ".join(kinfo.get("sponsor_name") or [])
            ceo = kinfo.get("ceo") or ""
            cio = kinfo.get("cio") or ""
            setup = kinfo.get("amc_setup_date") or ""
            trustee = kinfo.get("trustee_organisation") or ""

            facts.extend([
                f"=== OFFICIAL AMC FACTS: {fhouse} ===",
                f"AMC Name: {fhouse}",
                f"Total AMC AUM: ₹{float(tot_aum):,.2f} Cr" if tot_aum else "Total AMC AUM: N/A",
                f"Sponsors: {sponsors}",
                f"CEO: {ceo}",
                f"CIO: {cio}",
                f"Setup Date: {setup}",
                f"Trustee Organisation: {trustee}",
                "=== END OF AMC FACTS ==="
            ])

    return "\n".join(facts)


def _clean_html_to_text(html: str) -> str:
    # 1. Remove script and style blocks
    cleaned = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style.*?>.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # 2. Add structural markers for block elements to preserve line breaks
    # This helps Phase 4 identify section boundaries
    blocks = ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br", "header", "footer", "section", "article"]
    for tag in blocks:
        cleaned = re.sub(f"<{tag}[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(f"</{tag}>", "\n", cleaned, flags=re.IGNORECASE)

    # 3. Strip remaining tags
    no_tags = re.sub(r"<[^>]+>", " ", cleaned)
    
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
            facts = _extract_structured_facts(html)
            clean_body = _clean_html_to_text(html)
            text = (facts + "\n\n" + clean_body).strip() if facts else clean_body
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
