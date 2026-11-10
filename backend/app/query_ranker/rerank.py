import logging
from typing import List, Dict
from app.llm.llm_provider import generate_llm_text

logger = logging.getLogger(__name__)


def rerank(query: str, results: List[Dict]) -> List[Dict]:
    """
    Rerank retrieved chunks by relevance to the query using the LLM (Groq primary, Gemini fallback).

    Each item in `results` is {"chunk": str, "score": float}.
    Returns the list sorted from most to least relevant.
    """
    if not results:
        return results

    # Build a single prompt that asks the LLM to rank indices by relevance
    chunks_text = "\n\n".join(
        f"[{i}] {r['chunk']}" for i, r in enumerate(results)
    )

    prompt = f"""You are a relevance ranker. Given a user query and a list of text chunks,
return a comma-separated list of the chunk indices sorted from most to least relevant.
Output ONLY the comma-separated indices — no explanation, no extra text.

Query: {query}

Chunks:
{chunks_text}

Ranked indices (most to least relevant):"""

    try:
        raw_output = generate_llm_text(
            prompt=prompt,
            temperature=0.1,
            max_tokens=128,
        )

        ranked_indices = [
            int(idx.strip())
            for idx in raw_output.split(",")
            if idx.strip().isdigit()
        ]
        # Keep only valid indices and append any missing ones at the end
        seen = set()
        ordered = []
        for idx in ranked_indices:
            if 0 <= idx < len(results) and idx not in seen:
                ordered.append(results[idx])
                seen.add(idx)
        for idx in range(len(results)):
            if idx not in seen:
                ordered.append(results[idx])
        return ordered
    except Exception as e:
        logger.warning(f"Reranking failed: {e}. Falling back to original FAISS ordering.")
        return results
