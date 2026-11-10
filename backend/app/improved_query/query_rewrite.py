import logging
from app.llm.llm_provider import generate_llm_text

logger = logging.getLogger(__name__)


def rewrite_query(query: str) -> str:
    """
    Rewrite vague user queries into clear document-search queries.
    Uses Groq as primary LLM with Gemini as fallback.
    """
    prompt = f"""Rewrite the user's question so it becomes a clear search query
for retrieving information from a document.

Rules:
- Keep the meaning identical
- Expand vague references
- Do NOT answer the question

Examples:

User: what about the second one
Search Query: explain the second project mentioned in the document

User: traffic project
Search Query: explain the traffic management project in the document

User Question:
{query}

Search Query:"""

    try:
        rewritten = generate_llm_text(
            prompt=prompt,
            temperature=0.2,
            max_tokens=256,
        )
        return rewritten.strip()
    except Exception as e:
        logger.warning(f"Query rewrite failed: {e}. Using raw query.")
        return query
