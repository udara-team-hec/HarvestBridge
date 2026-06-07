import os
import time
import chromadb
from chromadb.utils import embedding_functions
from langchain_groq import ChatGroq
from src.schemas.models import ReportData

CHROMA_STORE_DIR = "rag/chroma_store"
COLLECTION_NAME = "harvestbridge_knowledge"


def query_knowledge_base(crop: str, region: str, top_k: int = 3) -> dict:
    """Searches ChromaDB for the most relevant document chunks."""

    chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    query = f"{crop} market prices middlemen negotiation {region} Africa"
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "distances", "metadatas"]
    )

    documents = results["documents"][0]
    distances = results["distances"][0]

    top_similarity = round(1 - (distances[0] / 2), 4) if distances else 0.0

    return {
        "chunks": documents,
        "top_similarity": top_similarity
    }


def analyze_knowledge(crop: str, region: str) -> dict:
    """Runs RAG retrieval and extracts structured market intelligence."""

    retrieval = query_knowledge_base(crop=crop, region=region)
    chunks = retrieval["chunks"]
    top_similarity = retrieval["top_similarity"]

    if not chunks:
        return {
            "typical_middleman_discount_pct": None,
            "historical_context": None,
            "similarity_score": 0.0
        }

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY")
    )
    structured_llm = llm.with_structured_output(ReportData)

    context = "\n\n---\n\n".join(chunks)
    prompt = f"""You are an agricultural market analyst.
    
Based ONLY on the following document excerpts, extract market intelligence 
for {crop} in {region}.

DOCUMENTS:
{context}

Extract:
1. The typical percentage discount middlemen apply when buying from farmers (if mentioned)
2. Any seasonal patterns, historical context, or market dynamics relevant to negotiation

If a piece of information is not explicitly stated in the documents, return null for that field.
Do NOT fabricate numbers. Only report what the documents say.

Set similarity_score to {top_similarity}."""

    result = structured_llm.invoke(prompt)
    result.similarity_score = top_similarity

    return {
        "typical_middleman_discount_pct": result.typical_middleman_discount_pct,
        "historical_context": result.historical_context,
        "similarity_score": result.similarity_score
    }


async def knowledge_agent_node(state: dict) -> dict:
    """The LangGraph wrapper for the Knowledge Engine."""
    start_time = time.time()

    crop_input = state.get("crop")
    region_input = state.get("region")

    try:
        report_result = analyze_knowledge(crop=crop_input, region=region_input)
        success = True
    except Exception as e:
        print(f"Knowledge agent error: {e}")
        report_result = {
            "typical_middleman_discount_pct": None,
            "historical_context": None,
            "similarity_score": 0.0
        }
        success = False

    execution_time = time.time() - start_time
    report_result["execution_log"] = {
        "agent_runtime": execution_time,
        "success_status": success,
        "token_usage": 0
    }

    return {"report_data": report_result}