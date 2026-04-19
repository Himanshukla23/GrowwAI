import faiss
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
VECTOR_INDEX_PATH = ROOT / "data" / "index" / "latest" / "vector_index.faiss"

def validate_index():
    if not VECTOR_INDEX_PATH.exists():
        print("Vector index not found yet.")
        return

    index = faiss.read_index(str(VECTOR_INDEX_PATH))
    dim = index.d
    num_vectors = index.ntotal

    print(f"Index Dimension: {dim}")
    print(f"Total Vectors: {num_vectors}")
    
    if dim == 768 and num_vectors == 242:
        print("Validation Passed: 242 vectors of 768 dimensions.")
    else:
        print("Validation Failed.")

if __name__ == "__main__":
    validate_index()
