"""
List Available ElevenLabs Voices
Helps you find your cloned voice ID
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def list_voices():
    """List all available voices"""
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not set in .env")
        return

    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        voices = response.json().get("voices", [])

        print("=" * 80)
        print(f"AVAILABLE VOICES ({len(voices)} total)")
        print("=" * 80)
        print()

        # Separate into built-in and custom
        builtin = [v for v in voices if v.get("category") != "cloned"]
        custom = [v for v in voices if v.get("category") == "cloned"]

        if custom:
            print("🎙️  YOUR CLONED VOICES:")
            print("-" * 80)
            for i, voice in enumerate(custom, 1):
                print(f"{i}. {voice['name']}")
                print(f"   Voice ID: {voice['voice_id']}")
                print(f"   Category: {voice.get('category', 'N/A')}")
                print(f"   Labels: {voice.get('labels', {})}")
                print()

        print("🔊 BUILT-IN VOICES:")
        print("-" * 80)
        for i, voice in enumerate(builtin[:10], 1):  # Show first 10
            print(f"{i}. {voice['name']}")
            print(f"   Voice ID: {voice['voice_id']}")
            print(f"   Labels: {voice.get('labels', {})}")
            print()

        if len(builtin) > 10:
            print(f"   ... and {len(builtin) - 10} more built-in voices")

        print("=" * 80)
        print("\n💡 To use a voice, update your .env file:")
        print("   ELEVENLABS_VOICE_ID=<voice_id_here>")
        print()

        # Show current setting
        current = os.getenv("ELEVENLABS_VOICE_ID", "Not set")
        current_voice = next((v for v in voices if v['voice_id'] == current), None)
        if current_voice:
            print(f"✅ Currently using: {current_voice['name']} ({current})")
        else:
            print(f"⚠️  Currently using: {current}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    list_voices()
