"""Tests for AI Marketing Script Generator."""

import pytest
from unittest.mock import patch, MagicMock
from modules.script_generator import generate_fallback_script, generate_marketing_script

def test_generate_fallback_script():
    data = {
        "business_name": "Lagos Buka",
        "category": "Food & Beverages / Restaurant",
        "product_name": "Smoky Jollof",
        "description": "Authentic firewood smoky jollof rice",
        "selling_points": "Spicy and delicious",
        "call_to_action": "Order today on WhatsApp!"
    }
    result = generate_fallback_script(data)
    assert "narration" in result
    assert "Lagos Buka" in result["narration"]
    assert "Smoky Jollof" in result["narration"]
    assert len(result["overlays"]) > 0
    assert len(result["search_keywords"]) > 0
    assert result["source"] == "fallback_template"

def test_generate_marketing_script_without_key():
    data = {
        "business_name": "Glow Essence",
        "category": "Beauty & Skincare",
        "product_name": "Vitamin C Serum",
        "description": "Brightening facial serum for glowing skin"
    }
    # No key provided
    result = generate_marketing_script(data, api_key="")
    assert "narration" in result
    assert "warning" in result
    assert result["source"] == "fallback_template"

@patch("google.genai.Client")
def test_generate_marketing_script_with_mocked_gemini(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock Gemini response with valid JSON
    mock_response = MagicMock()
    mock_response.text = '{"narration": "Looking for the best fashion in town? Check out Bella Chic today!", "overlays": ["Trendy Outfits", "Visit Bella Chic"], "search_keywords": ["african boutique", "fashion dress"]}'
    mock_client.models.generate_content.return_value = mock_response

    data = {
        "business_name": "Bella Chic",
        "category": "Fashion & Apparel",
        "product_name": "Evening Gown",
        "description": "Luxurious evening gowns",
        "duration": 15
    }

    result = generate_marketing_script(data, api_key="fake_key_123")
    assert result["source"] == "gemini"
    assert "Bella Chic" in result["narration"]
    assert "Trendy Outfits" in result["overlays"]
    assert "african boutique" in result["search_keywords"]
