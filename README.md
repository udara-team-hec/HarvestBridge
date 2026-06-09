# 🌍 HarvestBridge: Proactive AI for African Agriculture

[![Live Demo](https://huggingface.co/spaces/CharlyiE/HarvestBridge)
**HarvestBridge** is a multi-agent AI orchestration platform designed to arm African smallholder farmers with localized market intelligence and negotiation strategies to help combat the region's estimated 40% post-harvest loss rate.

## 💡 The Mission
Middlemen often leverage information asymmetry to artificially suppress farm-gate prices, forcing farmers to sell at a loss. HarvestBridge removes this blind spot by running a parallelized Directed Acyclic Graph (DAG) of AI agents to synthesize live commodity prices, weather risks, and supply-chain logistics into actionable negotiation leverage.

## 🏗️ Architecture & Agents
* **Price Agent:** Fetches and validates live commodity prices across regional markets.
* **Weather Agent:** Resolves geo-coordinates for real-time precipitation and humidity data.
* **Risk Agent:** Calculates a deterministic "Soil Saturation" and "Harvest Urgency" matrix.
* **Knowledge Agent:** Queries a custom ChromaDB RAG pipeline loaded with FAO/WFP supply chain reports.
* **Synthesizer:** Aggregates validated data into a plain-language negotiation brief for the farmer.

## 🛠️ Tech Stack
* **AI/Orchestration:** LangGraph, LangChain, Groq API (Llama-3.3-70b)
* **RAG:** ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`)
* **Data/State:** Pydantic, SQLite
* **App/Notifications:** Streamlit, APScheduler, Twilio (WhatsApp)

## 🚀 Quick Start (Local)

```bash
# 1. Clone and setup environment
git clone [https://github.com/](https://github.com/)[YOUR_GITHUB_USERNAME]/HarvestBridge.git
cd HarvestBridge
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Add API keys to .env
# GROQ_API_KEY, OPENWEATHERMAP_API_KEY, TWILIO setup

# 3. Init DB and run app
uv run python setup_db.py
uv run python ingest.py
uv run streamlit run app.py