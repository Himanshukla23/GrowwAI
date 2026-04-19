"""
Phase 10: Observability, Logging, and Evaluation Layer

Adheres to rag-architecture.md Section 4.9:
- Per-request structured logging: query class, retrieval candidates,
  citation URL, guardrail pass/fail, latency breakdown.
- In-memory metrics dashboard data (factual answer rate, refusal rate,
  citation coverage, freshness lag, unsupported queries).
- Retention/privacy: redact sensitive content before storage.
"""
import os
import re
import json
import time
import pathlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

# ── Log storage directory ────────────────────────────────────────────────────
LOG_DIR = ROOT / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# PII redaction patterns (same as guardrails, but for log scrubbing)
_PII_PATTERNS = {
    "pan": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "phone": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}


def _redact(text: str) -> str:
    """Redact PII from text before writing to logs."""
    for pii_type, pattern in _PII_PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", text)
    return text


class RequestLog:
    """Structured log entry for a single RAG request."""

    def __init__(self):
        self.start_time = time.time()
        self.data: Dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_class": None,          # factual / advisory / refusal / out-of-scope
            "original_query": None,
            "rewritten_query": None,
            "retrieval_candidates": [],    # chunk IDs
            "selected_chunk_ids": [],
            "citation_url": None,
            "guardrail_pre_pass": None,
            "guardrail_post_pass": None,
            "guardrail_violations": [],
            "latency": {
                "total_ms": 0,
                "retrieve_ms": 0,
                "rerank_ms": 0,
                "generate_ms": 0,
                "guardrail_ms": 0,
            },
            "answer_length": 0,
            "error": None,
        }

    def set_query(self, query: str, query_class: str):
        self.data["original_query"] = _redact(query)
        self.data["query_class"] = query_class

    def set_rewritten_query(self, rewritten: str):
        self.data["rewritten_query"] = _redact(rewritten)

    def set_retrieval(self, chunk_ids: List[str], selected_ids: List[str]):
        self.data["retrieval_candidates"] = chunk_ids
        self.data["selected_chunk_ids"] = selected_ids

    def set_citation(self, url: Optional[str]):
        self.data["citation_url"] = url

    def set_guardrail_pre(self, passed: bool):
        self.data["guardrail_pre_pass"] = passed

    def set_guardrail_post(self, passed: bool, violations: List[str] = None):
        self.data["guardrail_post_pass"] = passed
        self.data["guardrail_violations"] = violations or []

    def set_latency(self, phase: str, duration_ms: float):
        """phase: 'retrieve', 'rerank', 'generate', 'guardrail'"""
        key = f"{phase}_ms"
        if key in self.data["latency"]:
            self.data["latency"][key] = round(duration_ms, 2)

    def set_answer_length(self, length: int):
        self.data["answer_length"] = length

    def set_error(self, error: str):
        self.data["error"] = error

    def finalize(self):
        elapsed = (time.time() - self.start_time) * 1000
        self.data["latency"]["total_ms"] = round(elapsed, 2)
        return self.data


class ObservabilityStore:
    """
    Append-only structured log store with aggregate metrics.
    Logs are stored as JSONL (one JSON object per line) for easy parsing.
    """

    def __init__(self):
        self._log_file = LOG_DIR / "query_logs.jsonl"
        self._logs_in_memory: List[Dict] = []
        # Load existing logs into memory for metrics
        if self._log_file.exists():
            try:
                with open(self._log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self._logs_in_memory.append(json.loads(line))
            except Exception:
                pass  # Start fresh if file is corrupted

    def record(self, log: RequestLog) -> Dict:
        """Finalize and persist a request log entry."""
        entry = log.finalize()
        self._logs_in_memory.append(entry)
        # Append to JSONL file
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[Observability] Failed to write log: {e}")
        return entry

    def get_metrics(self) -> Dict:
        """
        Compute aggregate dashboard metrics (§4.9).

        Returns:
            {
                "total_queries": int,
                "factual_answer_rate": float,
                "refusal_rate": float,
                "citation_coverage": float,
                "avg_latency_ms": float,
                "guardrail_post_fail_rate": float,
                "query_class_breakdown": { "factual": int, ... },
                "unsupported_queries": int,
            }
        """
        total = len(self._logs_in_memory)
        if total == 0:
            return {
                "total_queries": 0,
                "factual_answer_rate": 0.0,
                "refusal_rate": 0.0,
                "citation_coverage": 0.0,
                "avg_latency_ms": 0.0,
                "guardrail_post_fail_rate": 0.0,
                "query_class_breakdown": {},
                "unsupported_queries": 0,
            }

        factual = sum(1 for l in self._logs_in_memory if l.get("query_class") == "factual")
        refusals = sum(
            1 for l in self._logs_in_memory
            if l.get("query_class") in ("advisory", "refusal", "pii")
        )
        with_citation = sum(1 for l in self._logs_in_memory if l.get("citation_url"))
        post_fails = sum(
            1 for l in self._logs_in_memory if l.get("guardrail_post_pass") is False
        )
        out_of_scope = sum(
            1 for l in self._logs_in_memory if l.get("query_class") == "out-of-scope"
        )

        latencies = [
            l["latency"]["total_ms"]
            for l in self._logs_in_memory
            if l.get("latency", {}).get("total_ms", 0) > 0
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Class breakdown
        breakdown: Dict[str, int] = {}
        for entry in self._logs_in_memory:
            cls = entry.get("query_class", "unknown")
            breakdown[cls] = breakdown.get(cls, 0) + 1

        return {
            "total_queries": total,
            "factual_answer_rate": round(factual / total, 4),
            "refusal_rate": round(refusals / total, 4),
            "citation_coverage": round(with_citation / total, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "guardrail_post_fail_rate": round(post_fails / total, 4),
            "query_class_breakdown": breakdown,
            "unsupported_queries": out_of_scope,
        }

    def get_recent_logs(self, n: int = 20) -> List[Dict]:
        """Return the N most recent log entries."""
        return self._logs_in_memory[-n:]


# ── Module-level singleton ───────────────────────────────────────────────────
observability = ObservabilityStore()


if __name__ == "__main__":
    print("=" * 60)
    print("OBSERVABILITY LAYER — SELF-TEST")
    print("=" * 60)

    store = ObservabilityStore()

    # Simulate a few requests
    for i, (query, qclass) in enumerate([
        ("What is the NAV of SBI Contra Fund?", "factual"),
        ("Should I invest in HDFC?", "advisory"),
        ("What is expense ratio of ICICI?", "factual"),
        ("Tell me about cricket", "out-of-scope"),
    ]):
        log = RequestLog()
        log.set_query(query, qclass)
        log.set_rewritten_query(query)
        log.set_retrieval(
            chunk_ids=[f"chunk_{i}_1", f"chunk_{i}_2"],
            selected_ids=[f"chunk_{i}_1"],
        )
        if qclass == "factual":
            log.set_citation("https://groww.in/mutual-funds/example")
        log.set_guardrail_pre(qclass == "factual")
        log.set_guardrail_post(True)
        log.set_latency("retrieve", 120 + i * 10)
        log.set_latency("generate", 800 + i * 50)
        log.set_answer_length(200)
        store.record(log)

    # Print metrics
    metrics = store.get_metrics()
    print("\nDashboard Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print(f"\nLog file: {store._log_file}")
    print(f"Total persisted entries: {len(store._logs_in_memory)}")
