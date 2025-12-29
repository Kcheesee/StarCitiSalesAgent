"""
Voice API Routes
Handles speech-to-text and text-to-speech endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ..services.voice_service import transcribe_audio, synthesize_speech, get_available_voices

router = APIRouter(prefix="/api/voice", tags=["voice"])


# ============================================================================
# Pydantic Models
# ============================================================================

class TranscriptionResponse(BaseModel):
    """Response from speech-to-text"""
    text: str
    success: bool = True


class SynthesisRequest(BaseModel):
    """Request for text-to-speech"""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM")


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using OpenAI Whisper

    Args:
        audio: Audio file (webm, mp3, wav, etc.)

    Returns:
        Transcribed text
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()

        # Transcribe using Whisper
        text = transcribe_audio(audio_bytes, audio.filename)

        return TranscriptionResponse(text=text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    """
    Convert text to speech using ElevenLabs

    Args:
        request: Text and voice settings

    Returns:
        Audio file (MP3)
    """
    try:
        # Synthesize speech
        audio_bytes = synthesize_speech(request.text, request.voice_id)

        # Return as audio response
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.get("/voices")
async def list_voices():
    """
    Get list of available ElevenLabs voices

    Returns:
        List of voice configurations
    """
    try:
        voices = get_available_voices()
        return {"voices": voices}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voices: {str(e)}"
        )
