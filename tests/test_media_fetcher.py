"""Tests for Stock Media Retrieval and Real Product Photo Retrieval."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from modules.media_fetcher import (
    generate_illustrative_scene,
    fetch_media_assets,
    search_pexels_photos
)

def test_generate_illustrative_scene():
    scene_path = generate_illustrative_scene(
        category="Fashion & Apparel",
        scene_index=0,
        aspect_ratio="9:16"
    )
    p = Path(scene_path)
    assert p.exists()
    assert p.stat().st_size > 1000
    p.unlink()

def test_fetch_media_assets_bundled_real_products():
    # Without Pexels API key and without user upload, it retrieves real bundled product photos
    assets = fetch_media_assets(
        keywords=["fashion dress"],
        category="Fashion & Apparel",
        aspect_ratio="9:16",
        num_scenes=2,
        api_key=""
    )
    assert len(assets) == 2
    for item in assets:
        assert item["type"] == "image"
        assert item["source"] in ("real_product_photo", "illustrative")
        p = Path(item["path"])
        assert p.exists()

def test_fetch_media_assets_user_uploaded_images(tmp_path):
    # Create fake user uploaded product image
    user_img = tmp_path / "my_dress.jpg"
    user_img.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 200)

    assets = fetch_media_assets(
        keywords=["ankara dress"],
        category="Fashion & Apparel",
        aspect_ratio="9:16",
        num_scenes=2,
        api_key="",
        user_uploaded_images=[str(user_img)]
    )
    assert len(assets) == 2
    assert assets[0]["source"] == "user_product_photo"
    assert assets[0]["path"] == str(user_img)

@patch("modules.media_fetcher.requests.get")
def test_search_pexels_photos_mock(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "photos": [
            {
                "id": 12345,
                "src": {"large2x": "https://images.pexels.com/photos/12345/test.jpg"}
            }
        ]
    }
    mock_get.return_value = mock_response

    results = search_pexels_photos("fashion", "mock_key", count=1)
    assert len(results) == 1
    assert results[0]["id"] == 12345
    assert results[0]["url"] == "https://images.pexels.com/photos/12345/test.jpg"
