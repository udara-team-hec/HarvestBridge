import os
import chromadb
from chromadb.utils import embedding_functions
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# --- Config ---
DOCUMENTS_DIR = "rag/documents"
CHROMA_STORE_DIR = "rag/chroma_store"
COLLECTION_NAME = "harvestbridge_knowledge"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128

def ingest_documents():
    """Loads PDFs, chunks them, embeds them, and stores in ChromaDB."""

    # 1. Load all PDFs from the documents folder
    print(f"Loading documents from {DOCUMENTS_DIR}...")
    reader = SimpleDirectoryReader(
        input_dir=DOCUMENTS_DIR,
        required_exts=[".pdf"]
    )
    documents = reader.load_data()
    print(f"Loaded {len(documents)} document pages.")

    # 2. Chunk into nodes
    print("Chunking documents...")
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} chunks.")

    # 3. Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Delete existing collection if re-ingesting
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print("Cleared existing collection.")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    # 4. Add chunks to ChromaDB in batches
    print("Embedding and storing chunks...")
    batch_size = 50
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i + batch_size]
        collection.add(
            documents=[node.text for node in batch],
            ids=[f"chunk_{i + j}" for j, _ in enumerate(batch)],
            metadatas=[{
                "source": node.metadata.get("file_name", "unknown"),
                "page": str(node.metadata.get("page_label", "unknown"))
            } for node in batch]
        )
        print(f"  Stored chunks {i} to {i + len(batch)}")

    print(f"\n✓ Ingestion complete. {len(nodes)} chunks stored in {CHROMA_STORE_DIR}")
    return len(nodes)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    ingest_documents()