import faiss
import numpy as np

from app.embeddings import embed_text
from app.session_store import get_session, _sessions


def retrieve(query: str, session_id: str | None = None, k: int = 5):
    session = get_session(session_id) if session_id else None

    # Fallback to the latest active session if session_id didn't match directly
    if not session and len(_sessions) > 0:
        session = next(reversed(_sessions.values()))

    if not session or "index" not in session or "chunks" not in session:
        return []

    index = session["index"]
    chunks = session["chunks"]

    if index.ntotal == 0 or len(chunks) == 0:
        return []

    query_vector = np.array([embed_text(query)], dtype="float32")
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, min(k, index.ntotal))
    results = []

    for j, i in enumerate(indices[0]):
        if i != -1 and i < len(chunks):
            results.append({
                "chunk": chunks[i],
                "score": float(scores[0][j])
            })

    return results
