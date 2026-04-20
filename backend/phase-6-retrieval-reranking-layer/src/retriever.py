"""
Phase 6: Retrieval and Re-ranking Layer

Handles fetching relevant chunks from ChromaDB for grounded generation.
Supports Cloud and Local Chroma databases natively based on the .env file.
Adheres to rag-architecture.md Section 4.4 and 10.1 (ChromaDB query API).
"""
import os
import pathlib
import sys
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load Environment
ROOT = pathlib.Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

# ChromaDB Config
CHROMA_LOCAL_DIR = ROOT / os.getenv("CHROMA_DB_DIR", "data/chroma")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "").strip()
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "").strip()
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "").strip()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "groww_mf_chunks_v4")

class Retriever:
    def __init__(self):
        """Initializes the ChromaDB Client and Embedding Function."""
        self.client = self._connect_chroma()
        
        print(f"[Retriever] Initializing Custom FastEmbed: {MODEL_NAME}")
        class CustomFastEmbed:
            def __init__(self, model_name):
                from fastembed import TextEmbedding
                cache_path = ROOT / "data" / "fastembed_cache"
                cache_path.mkdir(parents=True, exist_ok=True)
                self.model = TextEmbedding(model_name=model_name, cache_dir=str(cache_path))
            def name(self):
                return "all-MiniLM-L6-v2"
            def __call__(self, input):
                if isinstance(input, str):
                    input = [input]
                return list(self.model.embed(list(input)))
            def embed_query(self, input):
                return self(input)
            def embed_documents(self, input):
                return self(input)
        
        self.embedding_function = CustomFastEmbed(model_name=f"sentence-transformers/{MODEL_NAME}")
        
        try:
            self.collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"[Retriever] Successfully connected to collection '{COLLECTION_NAME}'. Total indexed chunks: {self.collection.count()}")
        except Exception as e:
            print(f"[Retriever] Failed to connect to collection '{COLLECTION_NAME}'. Make sure Phase 5 Indexer has run. Error: {e}")
            sys.exit(1)

    def _connect_chroma(self):
        """Connect to Cloud or Local ChromaDB based on .env credentials."""
        if CHROMA_API_KEY:
            print("[Retriever] Using ChromaDB Cloud connection...")
            kwargs = {"api_key": CHROMA_API_KEY}
            if CHROMA_TENANT: kwargs["tenant"] = CHROMA_TENANT
            if CHROMA_DATABASE: kwargs["database"] = CHROMA_DATABASE
            return chromadb.CloudClient(**kwargs)
        else:
            print(f"[Retriever] Using local ChromaDB at: {CHROMA_LOCAL_DIR}")
            if not CHROMA_LOCAL_DIR.exists():
                raise FileNotFoundError(f"Local ChromaDB not found at {CHROMA_LOCAL_DIR}. Please run Phase 5 Indexer first.")
            return chromadb.PersistentClient(path=str(CHROMA_LOCAL_DIR))

    def retrieve(self, query: str, top_k: int = 5, filters: dict = None, exact_phrase: str = None) -> list:
        """
        Retrieves top_k semantic matches from the vector database.
        
        :param query: Natural language user query.
        :param top_k: Number of chunks to retrieve.
        :param filters: Dict of metadata filters (e.g., {"amc_name": "SBI Mutual Fund"})
        :param exact_phrase: Substring that MUST appear in the document body.
        :return: List of evidence dictionaries containing text, metadata, and distance.
        """
        kwargs = {
            "query_texts": [query],
            "n_results": top_k
        }
        
        # 1. Apply Metadata Filters
        if filters:
            if len(filters) > 1:
                # Chroma requires $and operator when applying multiple distinct filters
                kwargs["where"] = {"$and": [{k: {"$eq": v}} for k, v in filters.items()]}
            else:
                kwargs["where"] = filters
                
        # 2. Apply Keyword/Full-Text Filter
        if exact_phrase:
            kwargs["where_document"] = {"$contains": exact_phrase}
            
        # 3. Query Execution
        results = self.collection.query(**kwargs)
        
        # 4. Format Results
        evidence = []
        if not results['documents'] or not results['documents'][0]:
            return evidence
            
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0]
        ids = results['ids'][0]
        
        for i in range(len(docs)):
            evidence.append({
                "chunk_id": ids[i],
                "text": docs[i],
                "metadata": metas[i],
                "distance": distances[i]
            })
            
        return evidence

if __name__ == "__main__":
    # Test script to validate Phase 6 retrieval works
    retriever = Retriever()
    
    test_query = "What is the exit load?"
    print(f"\n[Test Search] Query: '{test_query}'")
    
    # Example showing hybrid usage with semantic query + metadata filtering
    results = retriever.retrieve(
        query=test_query, 
        top_k=3,
        filters={"amc_name": "SBI Mutual Fund"} # Only searching within SBI funds
    )
    
    if not results:
        print("No results found.")
    else:
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} (Semantic Distance: {res['distance']:.4f}) ---")
            print(f"Source URL: {res['metadata'].get('source_url')}")
            print(f"Document Type: {res['metadata'].get('document_type')}")
            text_preview = res['text'].replace('\n', ' ').strip()
            print(f"Content Preview: {text_preview[:250]}...")
