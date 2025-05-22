from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from pathlib import Path
from app.llm_client import query_llm
from app.memory import MemoryStore

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Load environment variables from api/.env
load_dotenv(dotenv_path=ENV_PATH)

# Config
LLM_NAME = os.getenv("LLM_NAME")
LLM_URL = os.getenv("LLM_URL")
if not LLM_NAME or not LLM_URL:
    raise RuntimeError("LLM_NAME and LLM_URL environment variables must be set in api/.env or the environment.")
LLM_NAME = str(LLM_NAME)
LLM_URL = str(LLM_URL)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
MAX_FAISS_DISTANCE = 1.2

# Initialize FastAPI app
app = FastAPI()

API_PORT = os.getenv("API_PORT", "8000")
print(f"[INFO] API is running. Port: {API_PORT}")

# Load index and metadata
index_path = os.path.join(DATA_DIR, "support_index.faiss")
metadata_path = os.path.join(DATA_DIR, "support_metadata.json")
index = faiss.read_index(index_path)
with open(metadata_path, "r") as f:
    metadata = json.load(f)
ticket_ids = list(metadata.keys())

# Load embedding model
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

# In-memory conversation tracker
memory = MemoryStore()

class ChatRequest(BaseModel):
    session_id: str
    user_message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # Manual memory clear
    if req.user_message.lower().strip() in ["clear", "reset", "forget", "start over"]:
        memory.clear(req.session_id)
        return {"response": "🧹 Memory cleared. Ask me anything new!", "source_count": 0}

    # Embed query and search FAISS
    query_vec = embedder.encode([req.user_message]).astype("float32")
    D, I = index.search(query_vec, k=TOP_K)

    # Relevance check
    top_score = D[0][0]
    if top_score > MAX_FAISS_DISTANCE:
        return {
            "response": "❌ Sorry, I couldn't find any relevant support tickets for that question.",
            "source_count": 0
        }

    retrieved = [metadata[ticket_ids[i]] for i in I[0]]

    # Get session memory
    history = memory.get(req.session_id)

    # Construct prompt
    context = "\n\n".join(retrieved)
    full_prompt = f"""
You are a helpful support assistant.

Conversation history:
{history}

User question:
{req.user_message}

Relevant support tickets:
{context}

Based on the above, provide a helpful and accurate answer:
"""

    # Call LLM
    llm_response = query_llm(LLM_URL, LLM_NAME, full_prompt)

    # Save message to memory
    memory.append(req.session_id, f"User: {req.user_message}\nAssistant: {llm_response}")

    return {"response": llm_response, "source_count": len(retrieved)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(API_PORT), reload=True)
