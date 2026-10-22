"""Video Composition Engine using MoviePy and Pillow for high-speed promotional MP4 video production."""

import os
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import numpy as np
import PIL.Image as Image
from PIL import ImageDraw, ImageFont

# Monkeypatch Pillow 10+ compatibility for MoviePy 1.0.3
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips
)

from modules.config import (
    TEMP_DIR,
    DEFAULT_BG_MUSIC,
    ASPECT_RATIOS,
    DEFAULT_FPS,
    AUDIO_VOLUME_VOICE,
    AUDIO_VOLUME_BG_MUSIC
)

logger = logging.getLogger(__name__)

def get_system_font(size: int = 28) -> ImageFont.ImageFont:
    """Load high-quality bold system font on Windows or Linux (Streamlit Cloud), falling back to default."""
    font_candidates = [
        # Windows
        "arialbd.ttf",
        "segoeuib.ttf",
        "arial.ttf",
        "segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        # Linux (Streamlit Cloud / Debian / Ubuntu)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "DejaVuSans-Bold.ttf",
        "DejaVuSans.ttf",
        "FreeSansBold.ttf"
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()

def wrap_text(text: str, max_chars: int = 24) -> List[str]:
    """Wrap text to avoid running beyond the screen edges."""
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines or [text]

def fit_and_flatten_scene_image(
    img_path: str,
    target_w: int,
    target_h: int,
    business_name: str = "",
    caption_text: str = ""
) -> np.ndarray:
    """
    Load an image, fit/center-crop it to target dimensions, and pre-render
    the top branded badge and lower-third text card directly with Pillow.
    This provides ultra-fast rendering with zero per-frame compositing overhead.
    """
    with Image.open(img_path) as im:
        im = im.convert("RGB")
        iw, ih = im.size
        img_ratio = iw / ih
        target_ratio = target_w / target_h

        if img_ratio > target_ratio:
            # Scale by height, center crop width
            new_h = target_h
            new_w = int(iw * (target_h / ih))
            im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            im_canvas = im_resized.crop((left, 0, left + target_w, target_h))
        else:
            # Scale by width, center crop height
            new_w = target_w
            new_h = int(ih * (target_w / iw))
            im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_h) // 2
            im_canvas = im_resized.crop((0, top, target_w, top + target_h))

    # Add overlay layer
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Top persistent business badge
    if business_name:
        badge_font_size = max(18, int(target_w * 0.038))
        b_font = get_system_font(badge_font_size)
        badge_text = business_name.upper()
        bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 18, 8
        x1 = (target_w - tw) // 2 - pad_x
        y1 = int(target_h * 0.05)
        x2 = x1 + tw + pad_x * 2
        y2 = y1 + th + pad_y * 2
        
        # Pill background with vibrant cyan border
        draw.rounded_rectangle([x1, y1, x2, y2], radius=14, fill=(11, 19, 43, 220), outline=(56, 189, 248, 240), width=2)
        draw.text(((target_w - tw) // 2, y1 + pad_y - 2), badge_text, font=b_font, fill=(255, 255, 255, 255))

    # 2. Lower-third text caption card
    if caption_text:
        card_font_size = max(22, int(target_w * 0.046))
        c_font = get_system_font(card_font_size)
        lines = wrap_text(caption_text, max_chars=int(target_w / (card_font_size * 0.62)))
        
        line_height = int(card_font_size * 1.3)
        max_line_w = 0
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=c_font)
            lw = bbox[2] - bbox[0]
            if lw > max_line_w:
                max_line_w = lw

        pad_x, pad_y = 26, 16
        total_text_h = len(lines) * line_height
        card_w = max_line_w + pad_x * 2
        card_h = total_text_h + pad_y * 2
        
        x1 = (target_w - card_w) // 2
        y1 = int(target_h * 0.74)
        x2 = x1 + card_w
        y2 = y1 + card_h
        
        # Dark glass card with electric cyan border
        draw.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=(15, 23, 42, 230), outline=(56, 189, 248, 235), width=2)
        
        cur_y = y1 + pad_y
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=c_font)
            lw = bbox[2] - bbox[0]
            draw.text(((target_w - lw) // 2, cur_y), l, font=c_font, fill=(255, 255, 255, 255))
            cur_y += line_height

    # Composite overlay onto canvas
    im_canvas_rgba = im_canvas.convert("RGBA")
    flattened = Image.alpha_composite(im_canvas_rgba, overlay).convert("RGB")
    return np.array(flattened)

def create_text_overlay_image(
    text: str,
    width: int,
    height: int,
    position: str = "bottom",
    business_name: str = ""
) -> np.ndarray:
    """Helper for backwards compatibility in standalone tests."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if position == "top" and business_name:
        font = get_system_font(int(width * 0.038))
        draw.rounded_rectangle([50, 40, width - 50, 90], radius=14, fill=(11, 19, 43, 220), outline=(56, 189, 248), width=2)
        draw.text((width // 2, 65), business_name.upper(), font=font, fill=(255, 255, 255), anchor="mm")
    elif position == "bottom" and text:
        font = get_system_font(int(width * 0.046))
        draw.rounded_rectangle([30, int(height * 0.74), width - 30, int(height * 0.86)], radius=18, fill=(15, 23, 42, 230), outline=(56, 189, 248), width=2)
        draw.text((width // 2, int(height * 0.80)), text, font=font, fill=(255, 255, 255), anchor="mm")

    return np.array(img)

def fit_clip_to_dimensions(clip, target_w: int, target_h: int):
    """Crop and scale a video clip to fill target dimensions without distortion."""
    cw, ch = clip.size
    clip_ratio = cw / ch
    target_ratio = target_w / target_h

    if clip_ratio > target_ratio:
        scaled = clip.resize(height=target_h)
        sw, sh = scaled.size
        x_center = sw / 2
        final_clip = scaled.crop(x_center=x_center, width=target_w)
    else:
        scaled = clip.resize(width=target_w)
        sw, sh = scaled.size
        y_center = sh / 2
        final_clip = scaled.crop(y_center=y_center, height=target_h)

    return final_clip

def compose_promotional_video(
    media_assets: List[Dict[str, Any]],
    voiceover_path: str,
    voiceover_duration: float,
    overlays: List[str],
    business_name: str,
    aspect_ratio: str = "9:16",
    target_duration: int = 15,
    include_bg_music: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    High-speed Video Assembly Engine combining:
      - Sequenced visual assets (user product pictures, real product photos, or video clips)
      - Synchronized voiceover audio
      - Pre-rendered top branding badge and synchronized lower-third cards
      - Ambient background music with audio ducking
      - Lightning-fast MP4 rendering using FFmpeg
    """
    if progress_callback:
        progress_callback("Configuring video canvas and layout...", 0.10)

    ar_info = ASPECT_RATIOS.get(aspect_ratio, ASPECT_RATIOS["9:16"])
    target_w = ar_info["width"]
    target_h = ar_info["height"]

    # Final video duration matches voiceover + slight cushion so speech is never truncated
    final_duration = max(voiceover_duration + 0.4, float(target_duration))
    num_scenes = max(1, len(media_assets))
    scene_duration = final_duration / num_scenes

    if progress_callback:
        progress_callback("Pre-rendering scenes with branding and captions...", 0.30)

    scene_clips = []
    opened_clips = []

    try:
        for idx, asset in enumerate(media_assets):
            path = asset["path"]
            mtype = asset.get("type", "image")
            caption = overlays[idx] if idx < len(overlays) else ""

            if mtype == "video":
                # For video clips
                vclip = VideoFileClip(path).without_audio()
                opened_clips.append(vclip)
                if vclip.duration < scene_duration:
                    n_loops = int(np.ceil(scene_duration / max(0.1, vclip.duration)))
                    vclip = concatenate_videoclips([vclip] * n_loops)
                sub_clip = vclip.subclip(0, scene_duration)
                fitted = fit_clip_to_dimensions(sub_clip, target_w, target_h)
                scene_clips.append(fitted)
            else:
                # Pre-composite branding and caption directly with Pillow for 40x speedup
                flattened_arr = fit_and_flatten_scene_image(
                    img_path=path,
                    target_w=target_w,
                    target_h=target_h,
                    business_name=business_name,
                    caption_text=caption
                )
                iclip = ImageClip(flattened_arr).set_duration(scene_duration)
                opened_clips.append(iclip)
                scene_clips.append(iclip)

        if not scene_clips:
            raise RuntimeError("No visual scenes could be prepared for composition.")

        # Concatenate flat scenes with zero per-frame alpha blending overhead
        final_video = concatenate_videoclips(scene_clips, method="chain")
        final_video = final_video.set_duration(final_duration)

        if progress_callback:
            progress_callback("Mixing voiceover narration and background music...", 0.60)

        # Audio composition
        audio_layers = []
        
        # Narration audio
        voice_audio = AudioFileClip(voiceover_path).volumex(AUDIO_VOLUME_VOICE)
        opened_clips.append(voice_audio)
        audio_layers.append(voice_audio)

        # Background music
        if include_bg_music and DEFAULT_BG_MUSIC.exists():
            bg_music = AudioFileClip(str(DEFAULT_BG_MUSIC))
            opened_clips.append(bg_music)
            
            # Loop bg music if needed
            if bg_music.duration < final_duration:
                n_loops = int(np.ceil(final_duration / max(0.1, bg_music.duration)))
                bg_music = concatenate_audioclips([bg_music] * n_loops)
                
            bg_music = (
                bg_music
                .subclip(0, final_duration)
                .volumex(AUDIO_VOLUME_BG_MUSIC)
                .audio_fadein(0.8)
                .audio_fadeout(1.2)
            )
            audio_layers.append(bg_music)

        mixed_audio = CompositeAudioClip(audio_layers).set_duration(final_duration)
        final_video = final_video.set_audio(mixed_audio)

        if progress_callback:
            progress_callback("Rendering high-speed MP4 video with FFmpeg...", 0.75)

        output_filename = f"promo_video_{uuid.uuid4().hex[:8]}.mp4"
        output_path = TEMP_DIR / output_filename
        temp_audio = TEMP_DIR / f"temp_snd_{uuid.uuid4().hex[:8]}.m4a"

        # High-speed MP4 encoding with stillimage tuning and multi-threading
        final_video.write_videofile(
            str(output_path),
            fps=DEFAULT_FPS,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(temp_audio),
            remove_temp=False,
            preset="ultrafast",
            threads=4,
            ffmpeg_params=["-tune", "stillimage"],
            logger=None
        )

        # Verify output
        if not output_path.exists() or output_path.stat().st_size < 1000:
            raise RuntimeError("Video rendering failed: output file is missing or corrupted.")

        file_size_mb = round(output_path.stat().st_size / (1024 * 1024), 2)

        if progress_callback:
            progress_callback("Video generation completed!", 1.0)

        return {
            "status": "success",
            "video_path": str(output_path),
            "filename": output_filename,
            "duration": round(final_duration, 1),
            "file_size_mb": file_size_mb,
            "resolution": f"{target_w}x{target_h}",
            "aspect_ratio": aspect_ratio
        }

    finally:
        # Safely release MoviePy clips and file handles
        for c in opened_clips:
            try:
                c.close()
            except Exception:
                pass
        try:
            final_video.close()
        except Exception:
            pass
        # Clean up temporary audio file after handles are released
        try:
            if 'temp_audio' in locals() and temp_audio.exists():
                temp_audio.unlink()
        except Exception:
            pass
