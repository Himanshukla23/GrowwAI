import requests
import json

BASE_URL = "http://localhost:8000"

def test_pipeline():
    print(f"Connecting to {BASE_URL}...")
    
    # 1. Test Health
    health = requests.get(f"{BASE_URL}/health").json()
    print(f"[Health] Status: {health['status']}, Chunks: {health['indexed_chunks']}")

    # 2. Create Thread
    thread = requests.post(f"{BASE_URL}/threads").json()
    thread_id = thread['thread_id']
    print(f"[Thread] Created: {thread_id}")

    # 3. Test Factual Query
    query = "What is the expense ratio of SBI Contra Fund Direct Growth?"
    print(f"[Query] Sending: '{query}'")
    resp = requests.post(f"{BASE_URL}/chat/{thread_id}/query", json={"query": query})
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"[Response] Answer: {data['answer'][:100]}...")
        print(f"[Response] Chunks Used: {data['chunks_used']}")
        print(f"[Response] Intent: {data['intent']}")
    else:
        print(f"[Error] Status: {resp.status_code}, Detail: {resp.text}")

if __name__ == "__main__":
    test_pipeline()
