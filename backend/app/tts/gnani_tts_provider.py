import logging
import re
import requests
from app.config import (
    GNANI_API_KEY,
    GNANI_BASE_URL,
    GNANI_TTS_MODEL,
    GNANI_TTS_VOICE,
    GNANI_TTS_LANGUAGE,
)

logger = logging.getLogger(__name__)


AVAILABLE_VOICES = [
    "Shivani", "Lakshmi", "Kalpana", "Chetana", "Vasudha", "Riyaa", "Tarika",
    "Avinash", "Shubham", "Prakash", "Devansh", "Yashraj", "Harshad"
]


def _clean_for_speech(text: str) -> str:
    """Strip markdown symbols and formatting so speech synthesis sounds completely natural."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code backticks
    text = re.sub(r"`(.*?)`", r"\1", text)
    # Remove bold / italic asterisks and underscores
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
    # Remove markdown headers
    text = re.sub(r"#+\s*", "", text)
    # Remove bullet symbols (*, -, •)
    text = re.sub(r"^\s*[\*\-\•]\s*", "", text, flags=re.MULTILINE)
    # Normalize excess whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def text_to_speech(text: str, voice: str | None = None) -> bytes:
    """
    Synthesize text to speech using Gnani AI Timbre v3.0 (https://api.vachana.ai/api/v1/tts/inference).
    Allows user-specified voice with fallback to GNANI_TTS_VOICE or 'Shivani'.
    """
    if not text or not text.strip():
        return b""

    if not GNANI_API_KEY:
        logger.error("GNANI_API_KEY is not configured. Cannot synthesize speech.")
        return b""

    # Clean text of markdown formatting for natural, stutter-free pronunciation
    spoken_text = _clean_for_speech(text)
    if not spoken_text:
        return b""

    # Select voice
    selected_voice = GNANI_TTS_VOICE or "Shivani"
    if voice and voice.strip():
        cleaned_voice = voice.strip()
        # Case-insensitive match against available voices
        matched = next((v for v in AVAILABLE_VOICES if v.lower() == cleaned_voice.lower()), None)
        if matched:
            selected_voice = matched
        else:
            logger.warning(f"Voice '{cleaned_voice}' not in available voices, falling back to '{selected_voice}'.")

    try:
        url = f"{GNANI_BASE_URL}/api/v1/tts/inference"
        headers = {
            "X-API-Key-ID": GNANI_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": spoken_text,
            "voice": selected_voice,
            "model": GNANI_TTS_MODEL or "timbre-v3.0",
            "language": GNANI_TTS_LANGUAGE or "en-IN",
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 24000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        }

        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200 and len(response.content) > 100:
            return response.content
        else:
            logger.error(f"Gnani TTS returned HTTP {response.status_code}: {response.text[:200]}")
            return b""
    except Exception as e:
        logger.error(f"Gnani AI TTS (Timbre) request failed: {e}")
        return b""
