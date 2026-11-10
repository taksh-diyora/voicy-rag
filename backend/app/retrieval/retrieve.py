import faiss
import pickle
import numpy as np

from app.config import FAISS_INDEX_PATH, CHUNKS_PATH
from app.embeddings import embed_text

# Lazy-loaded globals — populated on first call to retrieve()
_index = None
_chunks = None


def _load_index():
    global _index, _chunks
    if _index is None:
        _index = faiss.read_index(FAISS_INDEX_PATH)
        with open(CHUNKS_PATH, "rb") as f:
            _chunks, _ = pickle.load(f)


def reset_index():
    """Force the next retrieve() call to reload index from disk."""
    global _index, _chunks
    _index = None
    _chunks = None


def retrieve(query: str, k: int = 5):

    _load_index()

    query_vector = np.array([embed_text(query)], dtype="float32")

    faiss.normalize_L2(query_vector)

    scores, indices = _index.search(query_vector, k)

    results = []

    for j, i in enumerate(indices[0]):

        if i != -1 and i < len(_chunks):

            results.append({
                "chunk": _chunks[i],
                "score": float(scores[0][j])
            })

    return results