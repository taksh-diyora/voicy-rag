import logging
import requests
from app.config import (
    GNANI_API_KEY,
    GNANI_BASE_URL,
    GNANI_STT_MODEL,
    GNANI_STT_LANGUAGE_CODE,
)

logger = logging.getLogger(__name__)


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio using Gnani AI Prisma v3.0 (https://api.vachana.ai/stt/v3).
    """
    if not audio_bytes:
        return ""

    if not GNANI_API_KEY:
        logger.error("GNANI_API_KEY is not configured. Cannot transcribe audio.")
        return ""

    try:
        url = f"{GNANI_BASE_URL}/stt/v3"
        headers = {
            "X-API-Key-ID": GNANI_API_KEY,
        }
        files = {
            "audio_file": ("audio.wav", audio_bytes, "audio/wav"),
        }
        data = {
            "language_code": GNANI_STT_LANGUAGE_CODE or "en-IN",
            "model": GNANI_STT_MODEL or "prisma-v3.0",
            "format": "transcribe",
        }

        response = requests.post(url, headers=headers, files=files, data=data, timeout=20)
        if response.status_code == 200:
            resp_json = response.json()
            transcript = resp_json.get("transcript") or resp_json.get("text", "")
            return transcript.strip() if transcript else ""
        else:
            logger.error(f"Gnani STT returned error HTTP {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        logger.error(f"Gnani AI STT (Prisma) request failed: {e}")
        return ""

