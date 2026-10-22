"""Tests for MoviePy Video Composition Engine."""

import pytest
from pathlib import Path
from modules.media_fetcher import generate_illustrative_scene
from modules.voice_generator import generate_voiceover
from modules.video_composer import (
    create_text_overlay_image,
    compose_promotional_video
)

def test_create_text_overlay_image():
    # Top badge
    top_overlay = create_text_overlay_image(
        text="",
        width=720,
        height=1280,
        position="top",
        business_name="Bella Chic"
    )
    assert top_overlay.shape == (1280, 720, 4)

    # Bottom caption
    bottom_overlay = create_text_overlay_image(
        text="Special 20% Discount This Week",
        width=720,
        height=1280,
        position="bottom"
    )
    assert bottom_overlay.shape == (1280, 720, 4)

def test_compose_promotional_video_end_to_end():
    # Prepare small real audio via gTTS
    voice = generate_voiceover("Welcome to Bella Chic fashion store!", preferred_provider="gtts")
    
    # Prepare 2 illustrative visual scenes
    scene1 = generate_illustrative_scene("Fashion & Apparel", 0, "9:16")
    scene2 = generate_illustrative_scene("Fashion & Apparel", 1, "9:16")

    media_assets = [
        {"type": "image", "path": scene1, "source": "illustrative"},
        {"type": "image", "path": scene2, "source": "illustrative"}
    ]

    result = compose_promotional_video(
        media_assets=media_assets,
        voiceover_path=voice["audio_path"],
        voiceover_duration=voice["duration"],
        overlays=["Handmade Ankara", "Order on WhatsApp"],
        business_name="Bella Chic",
        aspect_ratio="9:16",
        target_duration=5,  # Short 5s test duration for quick test execution
        include_bg_music=True
    )

    assert result["status"] == "success"
    video_path = Path(result["video_path"])
    assert video_path.exists()
    assert video_path.stat().st_size > 5000  # Valid MP4 video file
    assert result["duration"] > 0
    from modules.config import ASPECT_RATIOS
    expected_res = f"{ASPECT_RATIOS['9:16']['width']}x{ASPECT_RATIOS['9:16']['height']}"
    assert result["resolution"] == expected_res

    # Clean up test output and assets
    try:
        video_path.unlink()
        Path(voice["audio_path"]).unlink()
        Path(scene1).unlink()
        Path(scene2).unlink()
    except Exception:
        pass
