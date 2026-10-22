"""Tests for input validation routines."""

import pytest
from modules.validators import validate_business_inputs, validate_script

def test_validate_business_inputs_valid():
    valid_data = {
        "business_name": "Bella Chic",
        "category": "Fashion & Apparel",
        "product_name": "Ankara Kimono",
        "description": "Premium handmade African fashion jackets for stylish women.",
        "aspect_ratio": "9:16",
        "duration": 15
    }
    is_valid, errors = validate_business_inputs(valid_data)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_business_inputs_missing_fields():
    invalid_data = {
        "business_name": "",
        "product_name": "",
        "description": "Short",
        "aspect_ratio": "invalid_ratio",
        "duration": 200
    }
    is_valid, errors = validate_business_inputs(invalid_data)
    assert is_valid is False
    assert any("Business name is required" in e for e in errors)
    assert any("Product or service name is required" in e for e in errors)
    assert any("minimum 10 characters" in e for e in errors)
    assert any("Invalid aspect ratio" in e for e in errors)
    assert any("between 5 and 90 seconds" in e for e in errors)

def test_validate_script_valid():
    script = "Upgrade your wardrobe today with authentic African print jackets from Bella Chic! Order yours now."
    is_valid, errors = validate_script(script, target_duration=15)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_script_empty_or_too_short():
    is_valid, errors = validate_script("", target_duration=15)
    assert is_valid is False
    assert any("cannot be empty" in e for e in errors)

    is_valid, errors = validate_script("Hello buy now", target_duration=15)
    assert is_valid is False
    assert any("minimum 5 words" in e for e in errors)
