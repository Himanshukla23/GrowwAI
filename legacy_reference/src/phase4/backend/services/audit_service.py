from __future__ import annotations

import json
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = Path("data/phase4_request_logs.jsonl")


def write_audit_log(entry: dict[str, Any]) -> None:
    """
    Appends request-level metadata for operational visibility.
    Keeps payload compact and avoids logging secrets.
    """
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=True) + "\n")
