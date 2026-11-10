import os
from dotenv import load_dotenv

# Absolute directory paths
_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/app
_BACKEND_DIR = os.path.dirname(_BASE_DIR)              # backend

# Always load backend/.env first, then CWD .env if present
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))
load_dotenv()

# ── API Keys ──────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GNANI_API_KEY = os.getenv("GNANI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── LLM Models (Groq Primary, Google Gemini Fallback) ──
GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")

# ── Speech-to-Text (STT) — Gnani AI Prisma ────────────
GNANI_STT_MODEL = os.getenv("GNANI_STT_MODEL", "prisma-v3.0")
GNANI_STT_LANGUAGE_CODE = os.getenv("GNANI_STT_LANGUAGE_CODE", "en-IN")

# ── Text-to-Speech (TTS) — Gnani AI Timbre ────────────
GNANI_TTS_MODEL = os.getenv("GNANI_TTS_MODEL", "timbre-v3.0")
GNANI_TTS_VOICE = os.getenv("GNANI_TTS_VOICE", "Shivani")
GNANI_TTS_LANGUAGE = os.getenv("GNANI_TTS_LANGUAGE", "en-IN")

# ── Gnani Base URL ────────────────────────────────────
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai").rstrip("/")

# ── Embeddings (Local FastEmbed) ──────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# ── Absolute paths for local vector store and chunks ──
FAISS_INDEX_PATH = os.path.join(_BASE_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(_BASE_DIR, "chunks.pkl")
