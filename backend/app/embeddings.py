"""
Local embedding utility using fastembed (ONNX Runtime).
No PyTorch required — lightweight and low memory footprint.
Model is ~30 MB ONNX vs ~500 MB PyTorch, same 384-dim output.
"""

from fastembed import TextEmbedding
from app.config import EMBEDDING_MODEL, EMBEDDING_DIM

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(EMBEDDING_MODEL)
    return _model


def embed_text(text: str) -> list[float]:
    """Return a normalized 384-dim embedding for a single text string."""
    model = _get_model()
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()
