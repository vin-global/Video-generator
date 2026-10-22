"""Stock Media and Real Product Image Retrieval module."""

import os
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from PIL import Image, ImageDraw, ImageFont

from modules.config import (
    TEMP_DIR,
    ASSETS_DIR,
    ASPECT_RATIOS,
    get_pexels_api_key
)

logger = logging.getLogger(__name__)

__all__ = [
    "SAMPLE_PRODUCTS_DIR",
    "CATEGORY_PRODUCT_PHOTOS",
    "get_bundled_product_photos",
    "search_pexels_photos",
    "generate_illustrative_scene",
    "fetch_media_assets",
]

SAMPLE_PRODUCTS_DIR = ASSETS_DIR / "sample_products"

# Map business categories to bundled high-resolution real product photos
CATEGORY_PRODUCT_PHOTOS = {
    "Fashion & Apparel": [
        "fashion_ankara_kimono_1792645976033.jpg",
        "fashion_boutique_rack_1792646076545.jpg"
    ],
    "Food & Beverages / Restaurant": [
        "food_jollof_meal_1792645997474.jpg",
        "food_soup_meal_1792646017777.jpg"
    ],
    "Beauty & Skincare": [
        "skincare_cream_serum_1792646036062.jpg",
        "skincare_soap_bars_1792646055292.jpg"
    ],
    "Retail & Supermarket": [
        "food_jollof_meal_1792645997474.jpg",
        "fashion_boutique_rack_1792646076545.jpg"
    ],
    "Hair & Barber Salon": [
        "skincare_soap_bars_1792646055292.jpg",
        "skincare_cream_serum_1792646036062.jpg"
    ]
}

def get_bundled_product_photos(category: str) -> List[str]:
    """Retrieve bundled realistic product photos for a given category."""
    if not SAMPLE_PRODUCTS_DIR.exists():
        return []

    filenames = CATEGORY_PRODUCT_PHOTOS.get(category)
    if not filenames:
        # Fallback to any available sample product photos
        filenames = [
            "fashion_ankara_kimono_1792645976033.jpg",
            "food_jollof_meal_1792645997474.jpg",
            "skincare_cream_serum_1792646036062.jpg"
        ]

    matched_paths = []
    for fn in filenames:
        p = SAMPLE_PRODUCTS_DIR / fn
        if p.exists():
            matched_paths.append(str(p))

    # If category had only 1, grab others to ensure variety
    if len(matched_paths) < 2:
        for f in SAMPLE_PRODUCTS_DIR.glob("*.jpg"):
            sp = str(f)
            if sp not in matched_paths:
                matched_paths.append(sp)

    return matched_paths

def generate_illustrative_scene(
    category: str,
    scene_index: int,
    aspect_ratio: str,
    headline: str = "",
    subtext: str = ""
) -> str:
    """Fallback generator for decorative background if no images exist."""
    ar_info = ASPECT_RATIOS.get(aspect_ratio, ASPECT_RATIOS["9:16"])
    width = ar_info["width"]
    height = ar_info["height"]

    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, width - 20, height - 20], outline=(56, 189, 248), width=2)

    file_path = TEMP_DIR / f"illustrative_{uuid.uuid4().hex[:8]}.png"
    img.save(file_path, quality=95)
    return str(file_path)

def search_pexels_videos(
    query: str,
    api_key: str,
    orientation: str = "portrait",
    count: int = 3
) -> List[Dict[str, Any]]:
    """Search Pexels API for video clips."""
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": count,
        "orientation": orientation
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=12)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            results = []
            for v in videos:
                files = v.get("video_files", [])
                chosen_file = None
                for f in files:
                    if f.get("quality") == "hd" and f.get("link"):
                        chosen_file = f.get("link")
                        break
                if not chosen_file and files:
                    chosen_file = files[0].get("link")
                    
                if chosen_file:
                    results.append({
                        "id": v.get("id"),
                        "url": chosen_file,
                        "type": "video",
                        "duration": v.get("duration", 5)
                    })
            return results
    except Exception as e:
        logger.error(f"Pexels video search failed for query '{query}': {e}")
        
    return []

def search_pexels_photos(
    query: str,
    api_key: str,
    orientation: str = "portrait",
    count: int = 4
) -> List[Dict[str, Any]]:
    """Search Pexels API for stock photos."""
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": count,
        "orientation": orientation
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=12)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            results = []
            for p in photos:
                src = p.get("src", {})
                img_url = src.get("large2x") or src.get("large") or src.get("medium")
                if img_url:
                    results.append({
                        "id": p.get("id"),
                        "url": img_url,
                        "type": "image",
                        "duration": 4.0
                    })
            return results
    except Exception as e:
        logger.error(f"Pexels photo search failed for query '{query}': {e}")
        
    return []

def download_media_file(url: str, media_type: str) -> Optional[str]:
    """Download a remote media asset to temp directory."""
    ext = "mp4" if media_type == "video" else "jpg"
    target_path = TEMP_DIR / f"pexels_{uuid.uuid4().hex[:8]}.{ext}"
    
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
            if target_path.exists() and target_path.stat().st_size > 1024:
                return str(target_path)
    except Exception as e:
        logger.error(f"Failed to download media from {url}: {e}")
        
    return None

def fetch_media_assets(
    keywords: List[str],
    category: str,
    aspect_ratio: str = "9:16",
    num_scenes: int = 3,
    api_key: Optional[str] = None,
    user_uploaded_images: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve required visual assets for video composition.
    
    Priority:
    1. User's uploaded product images (front-and-center actual product)
    2. Live Pexels API videos / photos (if API key configured)
    3. Bundled real product photography from assets/sample_products/ (real clothes, food, creams/soaps)
    4. Illustrative fallback
    """
    key = api_key or get_pexels_api_key()
    orientation = ASPECT_RATIOS.get(aspect_ratio, {}).get("orientation", "portrait")
    
    media_items: List[Dict[str, Any]] = []

    # Priority 1: User Uploaded Product Pictures
    if user_uploaded_images:
        for img_path in user_uploaded_images:
            if len(media_items) >= num_scenes:
                break
            if Path(img_path).exists():
                media_items.append({
                    "type": "image",
                    "path": str(img_path),
                    "duration": 4.0,
                    "source": "user_product_photo"
                })

    # Priority 2: Pexels API (if key configured and more scenes needed)
    if key and len(media_items) < num_scenes:
        search_terms = list(keywords)
        if not search_terms:
            search_terms = [category.split("/")[0].strip()]

        for term in search_terms[:3]:
            if len(media_items) >= num_scenes:
                break
                
            # Search photos first for fast downloading and crisp display
            photos = search_pexels_photos(term, key, orientation=orientation, count=2)
            for p in photos:
                if len(media_items) >= num_scenes:
                    break
                local_path = download_media_file(p["url"], "image")
                if local_path:
                    media_items.append({
                        "type": "image",
                        "path": local_path,
                        "duration": 4.0,
                        "source": "pexels_photo"
                    })

    # Priority 3: Bundled Real Product Photos (Clothes, Meals, Creams & Soaps)
    if len(media_items) < num_scenes:
        bundled = get_bundled_product_photos(category)
        for b_img in bundled:
            if len(media_items) >= num_scenes:
                break
            media_items.append({
                "type": "image",
                "path": b_img,
                "duration": 4.0,
                "source": "real_product_photo"
            })

    # If user provided 1 photo and we need 3 scenes, repeat user's photo with variation
    if 0 < len(media_items) < num_scenes:
        existing = list(media_items)
        idx = 0
        while len(media_items) < num_scenes:
            item = existing[idx % len(existing)]
            media_items.append({
                "type": item["type"],
                "path": item["path"],
                "duration": 4.0,
                "source": item["source"]
            })
            idx += 1

    # Absolute fallback (if no files at all exist)
    while len(media_items) < num_scenes:
        scene_path = generate_illustrative_scene(
            category=category,
            scene_index=len(media_items),
            aspect_ratio=aspect_ratio
        )
        media_items.append({
            "type": "image",
            "path": scene_path,
            "duration": 4.0,
            "source": "illustrative"
        })

    return media_items
