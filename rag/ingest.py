from dotenv import load_dotenv
load_dotenv(override=True)

import os
import fitz  # pymupdf
import chromadb
from chromadb.utils import embedding_functions

# --- Config ---
DOCUMENTS_DIR = "rag/documents"
CHROMA_STORE_DIR = "rag/chroma_store"
COLLECTION_NAME = "harvestbridge_knowledge"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extracts text page by page using PyMuPDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if text and len(text) > 50:  # skip blank or near-blank pages
            pages.append({
                "text": text,
                "source": os.path.basename(pdf_path),
                "page": str(page_num + 1)
            })
    doc.close()
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Splits text into overlapping chunks by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_documents():
    """Loads PDFs, extracts text, chunks, embeds, and stores in ChromaDB."""

    # 0. Guard against empty folder
    if not os.path.exists(DOCUMENTS_DIR) or not any(
        f.endswith(".pdf") for f in os.listdir(DOCUMENTS_DIR)
    ):
        print(f"✗ No PDF files found in {DOCUMENTS_DIR}.")
        return 0

    # 1. Extract text from all PDFs
    print(f"Extracting text from PDFs in {DOCUMENTS_DIR}...")
    all_chunks = []
    chunk_id = 0

    for filename in os.listdir(DOCUMENTS_DIR):
        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(DOCUMENTS_DIR, filename)
        print(f"  Reading {filename}...")
        pages = extract_text_from_pdf(pdf_path)

        if not pages:
            print(f"  ⚠ No readable text found in {filename} — may be scanned/image PDF")
            continue

        print(f"  Extracted {len(pages)} pages with readable text")

        for page_data in pages:
            text_chunks = chunk_text(
                page_data["text"],
                CHUNK_SIZE,
                CHUNK_OVERLAP
            )
            for chunk in text_chunks:
                if len(chunk.strip()) > 30:  # skip tiny chunks
                    all_chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": chunk.strip(),
                        "source": page_data["source"],
                        "page": page_data["page"]
                    })
                    chunk_id += 1

    print(f"\nTotal readable chunks: {len(all_chunks)}")

    if not all_chunks:
        print("✗ No readable text extracted from any PDF.")
        print("  All documents appear to be scanned image PDFs.")
        print("  Download text-based versions from the same sources.")
        return 0

    # 2. Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print("Cleared existing collection.")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    # 3. Store in batches
    print("Embedding and storing chunks...")
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        collection.add(
            documents=[c["text"] for c in batch],
            ids=[c["id"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch]
        )
        print(f"  Stored chunks {i} to {i + len(batch)}")

    print(f"\n✓ Ingestion complete. {len(all_chunks)} chunks stored in {CHROMA_STORE_DIR}")
    return len(all_chunks)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    ingest_documents()