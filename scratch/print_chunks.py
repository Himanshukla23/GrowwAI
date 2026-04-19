import json
import sys

with open("c:/Users/himan/GrowwAI/data/processed/latest/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

target_ids = ["groww-004::7::phase-4-v1", "groww-000::6::phase-4-v1", "groww-017::5::phase-4-v1"]
for chunk in chunks:
    if chunk.get("chunk_id") in target_ids:
        print(f"\n--- {chunk.get('chunk_id')} ---")
        print(chunk.get("text"))
