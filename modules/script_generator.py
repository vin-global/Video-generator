"""AI Marketing Script Generation module using Google Gemini API."""

import json
import logging
from typing import Dict, Any, List, Optional
from modules.config import get_gemini_api_key

logger = logging.getLogger(__name__)

# Fallback smart templates for offline/keyless testing or graceful degradation
OFFLINE_TEMPLATES = {
    "Fashion & Apparel": {
        "hook": "Upgrade your wardrobe with style that stands out!",
        "middle": "At {business_name}, we bring you {product_name} crafted for comfort, elegance, and everyday confidence. {selling_points}",
        "cta": "Shop now at {business_name} and elevate your look today!"
    },
    "Food & Beverages / Restaurant": {
        "hook": "Craving something truly delicious and fresh?",
        "middle": "Welcome to {business_name}! Experience our mouthwatering {product_name}, prepared with love and the finest ingredients. {selling_points}",
        "cta": "Treat yourself today! Order from {business_name} now."
    },
    "Beauty & Skincare": {
        "hook": "Glow naturally with skincare that actually works!",
        "middle": "Discover {product_name} from {business_name}. Formulated to nourish, protect, and bring out your natural beauty. {selling_points}",
        "cta": "Get yours today and start your journey to radiant skin!"
    },
    "Retail & Supermarket": {
        "hook": "Everything you need, all in one place at unbeatable value!",
        "middle": "Visit {business_name} for our quality {product_name}. Fresh stock, great deals, and friendly service every single day. {selling_points}",
        "cta": "Visit {business_name} or call us today to get the best deals!"
    },
    "default": {
        "hook": "Looking for the best in quality and dependable service?",
        "middle": "{business_name} proudly introduces {product_name}. Designed to give you {description}. {selling_points}",
        "cta": "Contact {business_name} today and experience the difference!"
    }
}

def generate_fallback_script(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a high-quality localized marketing script without an API key."""
    category = data.get("category", "default")
    template = OFFLINE_TEMPLATES.get(category, OFFLINE_TEMPLATES["default"])
    
    b_name = data.get("business_name", "Our Business")
    p_name = data.get("product_name", "our signature product")
    desc = data.get("description", "quality products and services")
    selling_points = data.get("selling_points", "")
    if selling_points:
        sp_text = f"Enjoy {selling_points}."
    else:
        sp_text = "Delivering exceptional quality every time."
        
    cta = data.get("call_to_action") or template["cta"].format(business_name=b_name)
    
    script_text = (
        f"{template['hook']} "
        f"{template['middle'].format(business_name=b_name, product_name=p_name, description=desc, selling_points=sp_text)} "
        f"{cta}"
    )
    
    # Extract overlay phrases
    overlays = [
        f"Introducing {p_name}",
        "Top Quality Guaranteed",
        cta[:35] if len(cta) > 35 else cta
    ]
    
    search_keywords = [
        data.get("category", "business").split("/")[0].strip().lower(),
        p_name.lower(),
        "store shopping business"
    ]
    
    return {
        "narration": script_text,
        "overlays": overlays,
        "search_keywords": search_keywords,
        "source": "fallback_template"
    }

def generate_marketing_script(data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate an AI marketing script using Google Gemini API.
    
    Parameters:
        data: Dictionary of business details
        api_key: Optional override for Gemini API key
    
    Returns:
        Dictionary with:
          - narration (str): Spoken voiceover script
          - overlays (List[str]): 3-5 punchy on-screen caption phrases
          - search_keywords (List[str]): 3-5 keywords for Pexels media retrieval
          - source (str): 'gemini' or 'fallback_template'
    """
    key = api_key or get_gemini_api_key()
    
    if not key:
        logger.warning("No Gemini API key provided. Falling back to template generation.")
        res = generate_fallback_script(data)
        res["warning"] = "Generated using smart business template (GEMINI_API_KEY is not set)."
        return res

    duration = int(data.get("duration", 15))
    target_words = max(25, int(duration * 2.2))  # Comfortable voiceover pacing
    
    prompt = f"""
You are an expert commercial advertising copywriter for small businesses and local entrepreneurs.
Write a high-converting promotional video script for the following business:

- Business Name: {data.get('business_name')}
- Category: {data.get('category')}
- Product/Service: {data.get('product_name')}
- Description: {data.get('description')}
- Target Audience: {data.get('target_audience', 'General customers')}
- Key Selling Points: {data.get('selling_points', 'High quality, affordable, friendly service')}
- Desired Tone: {data.get('tone', 'Friendly & Persuasive')}
- Target Video Duration: {duration} seconds (around {target_words} words for clear speech)
- Call to Action: {data.get('call_to_action', 'Contact us today!')}

REQUIREMENTS:
1. The script must be natural, catchy, and speak directly to customers.
2. Hook the viewer in the first sentence.
3. Highlight genuine customer benefits (no exaggerated medical or legal guarantees).
4. Word count MUST be approximately {target_words} words (between {int(target_words * 0.8)} and {int(target_words * 1.15)} words).
5. Extract 3 to 4 punchy on-screen caption phrases (maximum 5 words each) to display over video scenes.
6. Provide 3 to 4 specific search keywords to find relevant stock footage on Pexels (e.g., 'fashion model dress', 'african boutique clothing', 'coffee shop barista').

Respond ONLY with a valid JSON object in this exact schema:
{{
  "narration": "Full spoken script text goes here without stage directions or brackets.",
  "overlays": ["Phrase 1", "Phrase 2", "Phrase 3"],
  "search_keywords": ["keyword 1", "keyword 2", "keyword 3"]
}}
"""

    try:
        from google import genai
        client = genai.Client(api_key=key)
        
        # Call Gemini 2.5 Flash for fast, creative, high-quality script generation
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        raw_text = (response.text or "").strip()
        
        # Clean potential markdown wrapping (e.g. ```json ... ```)
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
            
        parsed = json.loads(raw_text)
        
        narration = (parsed.get("narration") or "").strip()
        overlays = parsed.get("overlays") or []
        search_keywords = parsed.get("search_keywords") or []
        
        if not narration:
            raise ValueError("Empty narration in Gemini response.")
            
        return {
            "narration": narration,
            "overlays": overlays if overlays else [data.get('product_name', 'Featured Product')],
            "search_keywords": search_keywords if search_keywords else [data.get('category', 'business')],
            "source": "gemini"
        }
        
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}. Falling back to smart template.")
        fallback = generate_fallback_script(data)
        fallback["warning"] = f"Gemini API error ({str(e)}). Used smart business template instead."
        return fallback
