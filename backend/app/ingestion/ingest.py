import io
import os
import faiss
import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.embeddings import embed_batch
from app.session_store import update_session


# ── Helpers ─────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalize whitespace for better chunking."""
    return " ".join(text.split())


def _extract_text(reader: PdfReader) -> str:
    """Extract and concatenate text from all readable pages."""
    text = ""
    for page_idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        except Exception as e:
            print(f"Warning: could not extract text from page {page_idx + 1}: {e}")
    return _clean_text(text)


def _build_index(text: str, session_id: str):
    """Chunk text, batch-embed with FastEmbed, and store in FAISS session memory."""
    if not text or not text.strip():
        raise ValueError(
            "No extractable text was found in this PDF. "
            "If your document contains scanned pages or images, please copy and paste the text directly into the 'Notes & Drafts' tab."
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=60)
    chunks = splitter.split_text(text)
    if not chunks:
        raise ValueError(
            "Could not create text chunks from this document. Please ensure the document contains readable text."
        )

    print(f"      Created {len(chunks)} chunks")
    print(f"      Embedding all {len(chunks)} chunks in one batch...")
    embeddings = embed_batch(chunks)
    embeddings = np.array(embeddings, dtype="float32")

    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        raise ValueError("Failed to generate vector embeddings for document chunks.")

    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    print(f"      Index: {index.ntotal} vectors")
    
    # Save directly to RAM under the user's session ID
    update_session(session_id, index, chunks)
    return chunks, embeddings, index


# ── Public API ─────────────────────────────────────

def ingest_pdf_bytes(pdf_bytes: bytes, session_id: str, filename="document.pdf"):
    """Parse PDF bytes, extract text, and index for the given session."""
    if not session_id:
        session_id = "default"

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        raise ValueError(f"Could not parse PDF file: {e}. Please ensure it is a valid, uncorrupted PDF.")

    if len(reader.pages) == 0:
        raise ValueError("The uploaded PDF has 0 pages.")

    text = _extract_text(reader)
    chunks, embeddings, index = _build_index(text, session_id)

    return {
        "filename": filename,
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "dim": int(embeddings.shape[1])
    }


def ingest_text(text: str, session_id: str, title: str = "pasted text"):
    """Clean plain text and index for the given session."""
    if not session_id:
        session_id = "default"

    text = _clean_text(text)
    if not text:
        raise ValueError("Provided text is empty after cleaning.")

    chunks, embeddings, index = _build_index(text, session_id)

    return {
        "title": title,
        "characters": len(text),
        "chunks": len(chunks),
        "dim": int(embeddings.shape[1])
    }
