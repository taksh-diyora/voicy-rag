import asyncio
import logging
from fastapi import APIRouter, UploadFile, File, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.ingestion.ingest import ingest_pdf_bytes, ingest_text
from app.session_store import get_session

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def run_in_thread(func, *args, **kwargs):
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    x_session_id: str | None = Header(None)
):
    session_id = (x_session_id or "default").strip()

    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

    try:
        pdf_bytes = await file.read()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to read file: {e}"})

    if len(pdf_bytes) == 0:
        return JSONResponse(status_code=400, content={"error": "Uploaded file is empty."})
    
    if len(pdf_bytes) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": "File exceeds 10MB limit. Please compress your PDF to prevent memory issues."}
        )

    try:
        result = await run_in_thread(ingest_pdf_bytes, pdf_bytes, session_id, file.filename)
        return {"status": "success", **result}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.exception("Unexpected error during PDF ingestion")
        return JSONResponse(status_code=500, content={"error": f"Ingestion error: {str(e)}"})


class TextIngestRequest(BaseModel):
    text: str
    title: str = "Pasted Text"


@router.post("/ingest/text")
async def ingest_text_document(
    body: TextIngestRequest,
    x_session_id: str | None = Header(None)
):
    session_id = (x_session_id or "default").strip()

    if not body.text.strip():
        return JSONResponse(status_code=400, content={"error": "Text content is empty."})

    try:
        result = await run_in_thread(ingest_text, body.text, session_id, body.title)
        return {"status": "success", **result}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.exception("Unexpected error during text ingestion")
        return JSONResponse(status_code=500, content={"error": f"Ingestion error: {str(e)}"})


@router.get("/api/document")
async def document_status(x_session_id: str | None = Header(None)):
    """Return whether a document index is currently loaded in RAM for this session."""
    session_id = (x_session_id or "default").strip()
    loaded = bool(get_session(session_id))
    return {"loaded": loaded}
