"""Configuration and constants for the AI Video Generator."""

import os
from pathlib import Path
# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMP_DIR = PROJECT_ROOT / "temp"
ASSETS_DIR = PROJECT_ROOT / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
DEFAULT_BG_MUSIC = MUSIC_DIR / "ambient_gentle.wav"

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables (.env optional on cloud platforms like Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

def get_api_key(key_name: str, fallback_value: str = "") -> str:
    """Retrieve an API key from environment variables or Streamlit secrets if running."""
    # Check OS environment first
    val = os.getenv(key_name, "").strip()
    if val:
        return val
    # Check Streamlit secrets if Streamlit is imported and active
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return fallback_value

def get_gemini_api_key() -> str:
    return get_api_key("GEMINI_API_KEY")

def get_pexels_api_key() -> str:
    return get_api_key("PEXELS_API_KEY")

def get_elevenlabs_api_key() -> str:
    return get_api_key("ELEVENLABS_API_KEY")

def get_elevenlabs_voice_id() -> str:
    return get_api_key("ELEVENLABS_VOICE_ID", fallback_value="21m00Tcm4TlvDq8ikWAM")

# Video Aspect Ratios (width, height) - Optimized for high-speed rendering and crisp mobile display
ASPECT_RATIOS = {
    "9:16": {
        "label": "9:16 (Vertical • TikTok / Reels / Shorts)",
        "width": 540,
        "height": 960,
        "orientation": "portrait"
    },
    "1:1": {
        "label": "1:1 (Square • Instagram / Facebook Feeds)",
        "width": 600,
        "height": 600,
        "orientation": "square"
    },
    "16:9": {
        "label": "16:9 (Landscape • YouTube / Website)",
        "width": 960,
        "height": 540,
        "orientation": "landscape"
    }
}

# Business Categories
BUSINESS_CATEGORIES = [
    "Fashion & Apparel",
    "Food & Beverages / Restaurant",
    "Beauty & Skincare",
    "Retail & Supermarket",
    "Electronics & Gadgets",
    "Hair & Barber Salon",
    "Fitness & Wellness",
    "Professional & Home Services",
    "Other Small Business"
]

# Marketing Tones
MARKETING_TONES = [
    "Persuasive & Direct",
    "Friendly & Warm",
    "Energetic & Hype",
    "Professional & Trustworthy",
    "Premium & Luxurious"
]

# Video Durations (seconds)
SUPPORTED_DURATIONS = [15, 30, 45, 60]

# Video Composition Settings - Optimized for ultra-fast generation
DEFAULT_FPS = 20
MAX_MEDIA_SCENES = 8
AUDIO_VOLUME_VOICE = 1.0
AUDIO_VOLUME_BG_MUSIC = 0.12  # Subtle background level to keep voice crystal clear
