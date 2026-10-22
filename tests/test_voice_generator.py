"""Tests for Voiceover Generator."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.voice_generator import generate_voiceover, generate_voiceover_gtts

def test_generate_voiceover_gtts_creates_file():
    text = "Hello, welcome to Bella Chic fashion!"
    result = generate_voiceover(text, preferred_provider="gtts")
    assert result["status"] == "success"
    assert result["provider"] == "gtts"
    assert Path(result["audio_path"]).exists()
    assert Path(result["audio_path"]).stat().st_size > 0
    assert result["duration"] > 0

    # Cleanup temp test file
    try:
        Path(result["audio_path"]).unlink()
    except Exception:
        pass

def test_generate_voiceover_empty_text():
    with pytest.raises(ValueError):
        generate_voiceover("")

@patch("modules.voice_generator.requests.post")
def test_generate_voiceover_elevenlabs_mock(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_mp3_audio_data_stream_content"
    mock_post.return_value = mock_response

    with patch("modules.voice_generator.AudioFileClip") as mock_audio_clip:
        mock_instance = MagicMock()
        mock_instance.duration = 4.5
        mock_audio_clip.return_value = mock_instance

        result = generate_voiceover(
            script_text="Experience luxury today with our new brand.",
            api_key="mock_eleven_key",
            voice_id="mock_voice_id",
            preferred_provider="elevenlabs"
        )
        assert result["status"] == "success"
        assert result["provider"] == "elevenlabs"
        assert result["duration"] == 4.5
