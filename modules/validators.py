"""Input validation routines for the AI Video Generation workflow."""

from typing import Dict, Any, List, Tuple
from modules.config import ASPECT_RATIOS, SUPPORTED_DURATIONS

def validate_business_inputs(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate user inputs from the creation workspace form.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    business_name = (data.get("business_name") or "").strip()
    if not business_name:
        errors.append("Business name is required.")
    elif len(business_name) > 100:
        errors.append("Business name must be 100 characters or less.")

    product_name = (data.get("product_name") or "").strip()
    if not product_name:
        errors.append("Product or service name is required.")
    elif len(product_name) > 120:
        errors.append("Product name must be 120 characters or less.")

    description = (data.get("description") or "").strip()
    if not description:
        errors.append("Product or service description is required.")
    elif len(description) < 10:
        errors.append("Please provide at least a brief description (minimum 10 characters).")
    elif len(description) > 1000:
        errors.append("Description is too long (maximum 1000 characters).")

    aspect_ratio = data.get("aspect_ratio", "9:16")
    if aspect_ratio not in ASPECT_RATIOS:
        errors.append(f"Invalid aspect ratio '{aspect_ratio}'. Must be one of {list(ASPECT_RATIOS.keys())}.")

    duration = data.get("duration", 15)
    try:
        dur_int = int(duration)
        if dur_int < 5 or dur_int > 90:
            errors.append("Video duration must be between 5 and 90 seconds.")
    except (ValueError, TypeError):
        errors.append("Video duration must be a valid number.")

    return (len(errors) == 0, errors)

def validate_script(script: str, target_duration: int = 15) -> Tuple[bool, List[str]]:
    """
    Validate the marketing script before passing to audio and video composition.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    text = (script or "").strip()

    if not text:
        errors.append("Marketing script cannot be empty.")
        return (False, errors)

    word_count = len(text.split())
    if word_count < 5:
        errors.append("Script is too short (minimum 5 words required).")

    # Rough speaking rate: ~2.3 words per second
    # For a 15-second video, ~35-45 words is ideal; max ~90 words
    max_words_per_sec = 3.5
    max_allowed = int(target_duration * max_words_per_sec) + 30
    if word_count > max_allowed:
        errors.append(
            f"Script is very long ({word_count} words) for a {target_duration}-second video. "
            f"Consider trimming to under {max_allowed} words so narration fits comfortably."
        )

    return (len(errors) == 0, errors)
