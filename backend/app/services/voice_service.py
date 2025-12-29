"""
Voice Service - Speech-to-Text and Text-to-Speech
Handles voice processing with OpenAI Whisper and ElevenLabs
"""

import os
import io
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default to Rachel, or use custom voice
ELEVENLABS_MODEL = "eleven_turbo_v2_5"  # Fastest model with lowest latency

# Models
WHISPER_MODEL = "whisper-1"


def transcribe_audio(audio_file: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribe audio to text using OpenAI Whisper

    Args:
        audio_file: Audio file bytes
        filename: Original filename (for format detection)

    Returns:
        Transcribed text
    """
    try:
        # Create file-like object from bytes
        audio_io = io.BytesIO(audio_file)
        audio_io.name = filename

        # Call Whisper API
        response = openai_client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_io,
            response_format="text"
        )

        return response

    except Exception as e:
        print(f"❌ Whisper transcription error: {e}")
        raise


def synthesize_speech(text: str, voice_id: str = ELEVENLABS_VOICE_ID) -> bytes:
    """
    Convert text to speech using ElevenLabs

    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID

    Returns:
        Audio bytes (MP3)
    """
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your-elevenlabs-api-key-here":
        raise ValueError("ElevenLabs API key not configured")

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        data = {
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "optimize_streaming_latency": 3  # Maximum latency optimization (0-4, 4 is max)
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

        return response.content

    except Exception as e:
        print(f"❌ ElevenLabs synthesis error: {e}")
        raise


def get_available_voices() -> list:
    """
    Get list of available ElevenLabs voices

    Returns:
        List of voice dictionaries
    """
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your-elevenlabs-api-key-here":
        return []

    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json().get("voices", [])

    except Exception as e:
        print(f"❌ Error fetching voices: {e}")
        return []
