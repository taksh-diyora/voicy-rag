import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.voice import router as voice_router
from app.routes.ingest import router as ingest_router
from app.config import FAISS_INDEX_PATH, CHUNKS_PATH


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup: clear any stale index from a previous session ──
    # Users must explicitly upload a document every time the server starts.
    for path in (FAISS_INDEX_PATH, CHUNKS_PATH):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    yield
    # ── Shutdown (nothing to clean up) ──


app = FastAPI(
    title="Real-Time Voice RAG Agent",
    description="Voice RAG Agent powered by Gnani AI (Prisma STT & Timbre TTS), Groq LLM (Gemini fallback), and FAISS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcription", "X-Response-Text"],
)

app.include_router(voice_router, tags=["Voice"])
app.include_router(ingest_router, tags=["Ingest"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Voice RAG Agent is running"}


# Resolve frontend path relative to this file so it works from any CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.abspath(os.path.join(_BASE_DIR, "..", "..", "frontend"))
if not os.path.isdir(_FRONTEND_DIR):
    _FRONTEND_DIR = os.path.abspath(os.path.join(_BASE_DIR, "..", "frontend"))

if os.path.isdir(_FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
