import os
from dotenv import load_dotenv

load_dotenv()

# ── Vector database (Qdrant) ──────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "travel_guides")

# ── Embeddings (OpenAI; Groq does not offer an embeddings API) ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

# ── Chat LLM: 'groq' or 'openai' ──────────────────────────
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# llama-3.3-70b-versatile was retired by Groq on 16 Aug 2026 (free/developer tier)
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")

# ── Streamlit -> FastAPI ──────────────────────────────────
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
