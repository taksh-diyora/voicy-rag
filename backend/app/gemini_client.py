"""
LLM and embedding helper client.
Primary: Groq LLM + local FastEmbed embeddings.
Fallback: Google Gemini.
"""

from app.llm.llm_provider import generate_llm_text
from app.embeddings import embed_text


def embed_content(text: str, model: str = None) -> list:
    """Return a list[float] embedding for text."""
    return embed_text(text)


def generate_content(prompt: str, model: str = None, temperature: float = 0.3) -> str:
    """Send prompt to LLM (Groq primary, Gemini fallback)."""
    return generate_llm_text(prompt=prompt, temperature=temperature)
