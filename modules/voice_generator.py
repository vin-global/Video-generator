"""Voiceover Generation module supporting ElevenLabs API and Google Text-to-Speech (gTTS)."""

import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from gtts import gTTS
from moviepy.editor import AudioFileClip

from modules.config import (
    TEMP_DIR,
    get_elevenlabs_api_key,
    get_elevenlabs_voice_id
)

logger = logging.getLogger(__name__)

def generate_voiceover_elevenlabs(
    text: str,
    api_key: str,
    voice_id: str,
    output_path: Path
) -> bool:
    """Generate audio using ElevenLabs REST API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200 and response.content:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        logger.warning(f"ElevenLabs API error: {response.status_code} - {response.text}")
        return False

def generate_voiceover_gtts(
    text: str,
    output_path: Path
) -> bool:
    """Generate audio using Google Text-to-Speech (free fallback)."""
    tts = gTTS(text=text, lang="en", tld="com", slow=False)
    tts.save(str(output_path))
    return True

def generate_voiceover(
    script_text: str,
    api_key: Optional[str] = None,
    voice_id: Optional[str] = None,
    preferred_provider: str = "auto"
) -> Dict[str, Any]:
    """
    Generate voiceover audio from the confirmed marketing script.
    
    Parameters:
        script_text: Clean confirmed marketing script
        api_key: ElevenLabs API key (optional)
        voice_id: ElevenLabs Voice ID (optional)
        preferred_provider: 'auto', 'elevenlabs', or 'gtts'
        
    Returns:
        Dictionary with:
          - audio_path: Path to rendered audio file
          - duration: Float seconds
          - provider: 'elevenlabs' or 'gtts'
          - status: 'success' or 'error'
    """
    text = (script_text or "").strip()
    if not text:
        raise ValueError("Cannot generate voiceover from an empty script.")

    unique_id = uuid.uuid4().hex[:8]
    output_file = TEMP_DIR / f"voice_{unique_id}.mp3"

    chosen_provider = "gtts"
    el_key = api_key or get_elevenlabs_api_key()
    el_voice = voice_id or get_elevenlabs_voice_id()

    # Attempt ElevenLabs if configured or requested
    if preferred_provider in ("auto", "elevenlabs") and el_key:
        try:
            success = generate_voiceover_elevenlabs(text, el_key, el_voice, output_file)
            if success and output_file.exists() and output_file.stat().st_size > 0:
                chosen_provider = "elevenlabs"
            else:
                logger.warning("ElevenLabs generation unsuccessful. Falling back to gTTS.")
                generate_voiceover_gtts(text, output_file)
                chosen_provider = "gtts"
        except Exception as e:
            logger.error(f"ElevenLabs error: {e}. Falling back to gTTS.")
            generate_voiceover_gtts(text, output_file)
            chosen_provider = "gtts"
    else:
        # Use gTTS
        generate_voiceover_gtts(text, output_file)
        chosen_provider = "gtts"

    # Verify and measure duration
    if not output_file.exists() or output_file.stat().st_size == 0:
        raise RuntimeError("Voiceover generation failed: Audio file was not created.")

    try:
        audio_clip = AudioFileClip(str(output_file))
        duration = float(audio_clip.duration)
        audio_clip.close()
    except Exception as e:
        logger.error(f"Error measuring audio duration: {e}")
        duration = max(5.0, len(text.split()) / 2.3)

    return {
        "audio_path": str(output_file),
        "duration": duration,
        "provider": chosen_provider,
        "status": "success"
    }
