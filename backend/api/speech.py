"""
Speech API endpoints (Speech-to-Text & Text-to-Speech).

Wiederverwendbare Endpoints für alle Projekte:
- LifeChronicle: Geschichten per Sprache eingeben
- CV Matcher: Dokumente vorlesen
- Andere: Beliebige Text-/Audio-Verarbeitung
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.speech_service import speech_service


router = APIRouter(prefix="/speech", tags=["Speech"])


class TranscribeResponse(BaseModel):
    """Speech-to-Text response."""
    success: bool
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None


class SynthesizeRequest(BaseModel):
    """Text-to-Speech request."""
    text: str
    language: str = "de-DE"
    voice: Optional[str] = None
    speed: float = 1.0


class SynthesizeResponse(BaseModel):
    """Text-to-Speech response."""
    success: bool
    audio_url: str
    duration: Optional[float] = None


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "de-DE"
):
    """
    Convert speech to text (Speech-to-Text).

    Supports: MP3, WAV, OGG, WEBM
    Uses: Whisper (local) or browser Web Speech API

    Args:
        file: Audio file
        language: Language code (de-DE, en-US, es-ES)

    Returns:
        Transcribed text with confidence score

    Example:
        ```python
        # Frontend usage with browser API
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'de-DE';
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            // Use text...
        };
        ```
    """
    try:
        # Read audio bytes
        audio_bytes = await file.read()

        # Transcribe using Whisper (local)
        result = await speech_service.transcribe(
            audio_bytes=audio_bytes,
            language=language
        )

        return TranscribeResponse(
            success=True,
            text=result['text'],
            language=result.get('language'),
            confidence=result.get('confidence')
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_text(request: SynthesizeRequest):
    """
    Convert text to speech (Text-to-Speech).

    Uses: Browser TTS API (client-side, local)
    or pyttsx3/gTTS (server-side)

    Args:
        request: Text and voice settings

    Returns:
        Audio URL or file path

    Example (Frontend - preferred for DSGVO):
        ```javascript
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'de-DE';
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
        ```

    Example (Backend):
        ```python
        response = await speech_service.synthesize(
            text="Hallo Welt",
            language="de-DE"
        )
        ```
    """
    try:
        result = await speech_service.synthesize(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed
        )

        return SynthesizeResponse(
            success=True,
            audio_url=result['audio_url'],
            duration=result.get('duration')
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices.

    Returns voices grouped by language.
    """
    try:
        voices = speech_service.get_voices()
        return {
            "success": True,
            "voices": voices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
