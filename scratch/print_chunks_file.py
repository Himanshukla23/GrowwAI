import json

with open("c:/Users/himan/GrowwAI/data/processed/latest/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

target_ids = ["groww-004::7::phase-4-v1", "groww-000::6::phase-4-v1", "groww-017::5::phase-4-v1"]
with open("c:/Users/himan/GrowwAI/scratch/output.txt", "w", encoding="utf-8") as out:
    for chunk in chunks:
        if chunk.get("chunk_id") in target_ids:
            out.write(f"\n--- {chunk.get('chunk_id')} ---\n")
            out.write(chunk.get("text") + "\n")
