import logging
from app.config import (
    GROQ_API_KEY,
    GEMINI_API_KEY,
    GROQ_LLM_MODEL,
    GEMINI_LLM_MODEL,
)

logger = logging.getLogger(__name__)

# Lazy initialization of clients
_groq_client = None
_gemini_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and GROQ_API_KEY:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize Groq client: {e}")
    return _groq_client


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        try:
            from google import genai
            _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
    return _gemini_client


def generate_llm_text(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Generate text using Groq as primary LLM, with automatic fallback to Google Gemini.
    """
    # ── 1. Primary: Groq ──────────────────────────────────────────────
    groq_client = _get_groq_client()
    if groq_client:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = groq_client.chat.completions.create(
                model=GROQ_LLM_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception as e:
            logger.warning(f"Groq LLM call ({GROQ_LLM_MODEL}) failed: {e}. Falling back to Google Gemini...")

    # ── 2. Fallback: Google Gemini ────────────────────────────────────
    gemini_client = _get_gemini_client()
    if gemini_client:
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            if system_prompt:
                config.system_instruction = system_prompt

            response = gemini_client.models.generate_content(
                model=GEMINI_LLM_MODEL,
                contents=prompt,
                config=config,
            )
            if response.text and response.text.strip():
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini fallback LLM call ({GEMINI_LLM_MODEL}) failed: {e}")

    raise RuntimeError("Both primary (Groq) and fallback (Gemini) LLM calls failed. Please check your API keys.")

