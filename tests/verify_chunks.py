from dotenv import load_dotenv
load_dotenv(override= True)
import chromadb
from chromadb.utils import embedding_functions

CHROMA_STORE_DIR = "rag/chroma_store"
COLLECTION_NAME = "harvestbridge_knowledge"

def verify_chunks():
    chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    total = collection.count()
    print(f"Total chunks in store: {total}")
    print()

    # Test query 1 — Nigeria maize middlemen
    print("=== Query: Nigeria maize middlemen ===")
    results = collection.query(
        query_texts=["maize market prices middlemen Nigeria"],
        n_results=3,
        include=["documents", "distances", "metadatas"]
    )
    for i, (doc, dist, meta) in enumerate(zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0]
    )):
        similarity = round(1 - (dist / 2), 4)
        print(f"\nResult {i+1} | similarity={similarity} | source={meta.get('source')} | page={meta.get('page')}")
        print(f"Text preview: {doc[:300]}")
        print("---")

    # Test query 2 — Ethiopia teff farmers
    print("\n=== Query: Ethiopia teff farmers price ===")
    results = collection.query(
        query_texts=["teff price farmers Ethiopia market"],
        n_results=3,
        include=["documents", "distances", "metadatas"]
    )
    for i, (doc, dist, meta) in enumerate(zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0]
    )):
        similarity = round(1 - (dist / 2), 4)
        print(f"\nResult {i+1} | similarity={similarity} | source={meta.get('source')} | page={meta.get('page')}")
        print(f"Text preview: {doc[:300]}")
        print("---")

    # Test query 3 — road access transport costs
    print("\n=== Query: road access transport costs harvest ===")
    results = collection.query(
        query_texts=["road access transport costs harvest season"],
        n_results=3,
        include=["documents", "distances", "metadatas"]
    )
    for i, (doc, dist, meta) in enumerate(zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0]
    )):
        similarity = round(1 - (dist / 2), 4)
        print(f"\nResult {i+1} | similarity={similarity} | source={meta.get('source')} | page={meta.get('page')}")
        print(f"Text preview: {doc[:300]}")
        print("---")


if __name__ == "__main__":
    verify_chunks()