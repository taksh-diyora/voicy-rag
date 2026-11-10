from fastapi import APIRouter, UploadFile, File, Header, Form
from fastapi.responses import Response
from pydantic import BaseModel
from urllib.parse import quote
import base64

from app.stt.gnani_stt_provider import transcribe_audio
from app.llm.generate import generate_answer
from app.tts.gnani_tts_provider import text_to_speech, AVAILABLE_VOICES

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    tts: bool = False
    voice: str | None = None


def _safe_header(value: str) -> str:
    """Encode string for HTTP header-safe ASCII."""
    return quote(value.strip().replace("\n", " ").replace("\r", " "), safe=" .,!?-_()'\"")


@router.get("/api/voices")
def list_voices():
    """Return the list of available Timbre v3.0 neural voices."""
    return {
        "voices": AVAILABLE_VOICES,
        "default": "Shivani",
    }


@router.post("/chat")
async def chat_query(req: ChatRequest, x_session_id: str | None = Header(None)):
    session_id = (x_session_id or "default").strip()
    answer = await generate_answer(req.message, session_id)
    res = {"question": req.message, "answer": answer}
    if req.tts:
        audio_response = await text_to_speech(answer, voice=req.voice)
        if audio_response:
            media_type = "audio/wav" if audio_response.startswith(b"RIFF") else "audio/mpeg"
            res["audio_base64"] = base64.b64encode(audio_response).decode("utf-8")
            res["audio_mime"] = media_type
    return res


@router.post("/voice")
async def voice_query(
    audio: UploadFile = File(...),
    voice: str | None = Form(None),
    x_session_id: str | None = Header(None)
):
    session_id = (x_session_id or "default").strip()
    question = transcribe_audio(await audio.read())
    answer = await generate_answer(question, session_id)
    audio_response = await text_to_speech(answer, voice=voice)
    media_type = "audio/wav" if audio_response.startswith(b"RIFF") else "audio/mpeg"

    return Response(
        content=audio_response,
        media_type=media_type,
        headers={
            "X-Transcription": _safe_header(question),
            "X-Response-Text": _safe_header(answer),
        },
    )


@router.post("/voice/text")
async def voice_query_text(audio: UploadFile = File(...)):
    """Transcribes audio and returns the text (for chat flow injection)."""
    return {"question": transcribe_audio(await audio.read())}
