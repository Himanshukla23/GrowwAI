import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Dict


ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRAPER_ENTRY = ROOT / "backend" / "phase-2-scraping-service" / "src" / "scraper.py"
PROCESSOR_ENTRY = ROOT / "backend" / "phase-4-document-processing-normalization" / "src" / "processor.py"
INDEXER_ENTRY = ROOT / "backend" / "phase-5-indexing-layer" / "src" / "indexer.py"
SCHEDULER_LOG_DIR = ROOT / "data" / "scheduler-runs"


def _run_scraper(fail_on_errors: bool) -> int:
    cmd = [sys.executable, str(SCRAPER_ENTRY)]
    if fail_on_errors:
        cmd.append("--fail-on-errors")
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return proc.returncode


def _run_processor() -> int:
    cmd = [sys.executable, str(PROCESSOR_ENTRY)]
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return proc.returncode


def _run_indexer() -> int:
    cmd = [sys.executable, str(INDEXER_ENTRY)]
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return proc.returncode


def _write_scheduler_run(status: str, exit_code: int) -> None:
    SCHEDULER_LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc)
    payload: Dict = {
        "timestamp_utc": timestamp.isoformat(),
        "status": status,
        "exit_code": exit_code,
        "trigger_source": "github_actions_or_manual",
        "scheduler_version": "phase-1-v1",
    }
    out_file = SCHEDULER_LOG_DIR / f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 scheduler refresh trigger.")
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Fail workflow when scraping service has URL failures.",
    )
    args = parser.parse_args()

    scraper_code = _run_scraper(fail_on_errors=args.fail_on_errors)
    processor_code = 0
    indexer_code = 0
    
    if scraper_code == 0:
        processor_code = _run_processor()
        if processor_code == 0:
            indexer_code = _run_indexer()
    
    overall_code = scraper_code or processor_code or indexer_code
    status = "success" if overall_code == 0 else "failed"
    _write_scheduler_run(status=status, exit_code=overall_code)
    print(f"[scheduler] refresh_completed status={status} exit_code={overall_code}")
    sys.exit(overall_code)


if __name__ == "__main__":
    main()
