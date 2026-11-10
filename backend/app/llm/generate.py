import asyncio
import logging

from app.llm.llm_provider import generate_llm_text
from app.retrieval.retrieve import retrieve

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a helpful voice assistant. Make use of the provided document context to answer questions.
If the provided context does not contain the answer or is not sufficient to answer the question, clearly state before answering: "That information is outside the provided document, but here is what I know:" and answer from your training knowledge.
Keep answers concise and conversational since they will be read aloud."""


# Python 3.8+ thread pool executor helper
async def run_in_thread(func, *args, **kwargs):
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


_conversation_history = []


from app.session_store import get_session, update_history

async def generate_answer(question: str, session_id: str) -> str:
    """
    Full RAG step (Optimized):
      1. Retrieve relevant chunks for `question` using session_id
      2. Compose a prompt with the retrieved context and session history
      3. Call LLM directly and return the answer text
    """
    # Retrieval is blocking (FAISS + local embeddings) — run in a thread
    docs = await run_in_thread(retrieve, question, session_id)

    context = "\n\n".join(d["chunk"] for d in docs)

    history_text = ""
    session = get_session(session_id)
    if session and session["history"]:
        history_text = "Recent Conversation History:\n"
        for role, text in session["history"]:
            history_text += f"{role.capitalize()}: {text}\n"
        history_text += "\n"

    prompt = f"""Context from document:
{context}

{history_text}User question: {question}

Answer:"""

    def _call():
        return generate_llm_text(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1024,
        )

    try:
        answer = await run_in_thread(_call)
    except Exception as e:
        logger.error(f"Error in generate_answer: {e}")
        answer = "I apologize, but I encountered an error while retrieving the answer. Please check your model API keys."

    update_history(session_id, "user", question)
    update_history(session_id, "assistant", answer)

    return answer
