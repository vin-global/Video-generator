"""
AI-POWERED AUTOMATIC VIDEO GENERATION SYSTEM FOR SMALL BUSINESSES
Streamlit Web Application Entrypoint
"""

import os
import sys
import uuid
from pathlib import Path
import streamlit as st

# Set page configuration early so error banners render cleanly
st.set_page_config(
    page_title="AI Video Generator for Small Businesses",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure project root is in Python module search path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safety check for missing modules directory on cloud deployments (e.g. partial GitHub uploads)
modules_dir = PROJECT_ROOT / "modules"
if not modules_dir.exists():
    st.error(
        "### ⚠️ Missing `modules/` Folder in Deployment\n\n"
        "Streamlit Cloud cannot locate the `modules/` directory.\n\n"
        "**How to fix:**\n"
        "1. When uploading to GitHub, please ensure you upload or push the entire project repository, including the `modules/` and `assets/` directories.\n"
        "2. If pushing via git: `git add . && git commit -m 'Include modules and assets' && git push`."
    )
    st.stop()

try:
    from modules.config import (
        ASPECT_RATIOS,
        BUSINESS_CATEGORIES,
        MARKETING_TONES,
        SUPPORTED_DURATIONS,
        get_gemini_api_key,
        get_pexels_api_key,
        get_elevenlabs_api_key,
        get_elevenlabs_voice_id
    )
    from modules.validators import validate_business_inputs, validate_script
    from modules.script_generator import generate_marketing_script
    from modules.voice_generator import generate_voiceover
    from modules.media_fetcher import fetch_media_assets, get_bundled_product_photos
    from modules.video_composer import compose_promotional_video
except Exception as e:
    st.error(
        f"### ⚠️ Dependency or Import Error\n\n"
        f"**Error Details:** `{e}`\n\n"
        f"**Troubleshooting:**\n"
        f"- Ensure your GitHub repository has the updated `requirements.txt`.\n"
        f"- Click **Manage app** in the bottom-right corner of Streamlit Cloud to see detailed logs."
    )
    st.stop()

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark_blue"  # Options: 'dark_blue' or 'clean_white'

if "current_step" not in st.session_state:
    st.session_state.current_step = 1  # 1: Details, 2: Script, 3: Generate, 4: Preview

if "business_data" not in st.session_state:
    st.session_state.business_data = {
        "business_name": "Bella Chic Fashion",
        "category": "Fashion & Apparel",
        "product_name": "Handmade Ankara Kimono",
        "description": "Stunning authentic African print kimono jackets tailored with vibrant cotton fabrics for modern everyday elegance.",
        "target_audience": "Stylish women looking for unique, comfortable statement wear",
        "selling_points": "100% premium cotton, breathable, free delivery in Lagos, custom sizing",
        "tone": "Friendly & Warm",
        "aspect_ratio": "9:16",
        "duration": 15,
        "call_to_action": "Order now on WhatsApp or visit our Lagos store!",
        "include_bg_music": True
    }

if "user_product_photos" not in st.session_state:
    st.session_state.user_product_photos = []

if "script_result" not in st.session_state:
    st.session_state.script_result = None

if "confirmed_script" not in st.session_state:
    st.session_state.confirmed_script = ""

if "generated_video" not in st.session_state:
    st.session_state.generated_video = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Quick business sample templates for easy one-click testing
SAMPLE_BUSINESSES = {
    "👗 Fashion Boutique": {
        "business_name": "Bella Chic Fashion",
        "category": "Fashion & Apparel",
        "product_name": "Handmade Ankara Kimono",
        "description": "Stunning authentic African print kimono jackets tailored with vibrant cotton fabrics for modern everyday elegance.",
        "target_audience": "Stylish women looking for unique statement outfits",
        "selling_points": "100% premium cotton, breathable, free delivery, custom sizing",
        "tone": "Friendly & Warm",
        "aspect_ratio": "9:16",
        "duration": 15,
        "call_to_action": "Order now on WhatsApp or visit our Lagos store!"
    },
    "🍲 Local Kitchen & Meals": {
        "business_name": "Mama T's Gourmet Kitchen",
        "category": "Food & Beverages / Restaurant",
        "product_name": "Smoky Jollof & Grilled Chicken Platter",
        "description": "Authentic firewood smoky jollof rice served with spiced tender grilled chicken, sweet fried plantains, and rich soups.",
        "target_audience": "Food lovers craving rich, hot, homemade African comfort meals",
        "selling_points": "Freshly prepared daily, rich spicy aroma, fast delivery under 30 mins",
        "tone": "Energetic & Hype",
        "aspect_ratio": "9:16",
        "duration": 15,
        "call_to_action": "Order lunch now on WhatsApp or call for delivery!"
    },
    "✨ Skincare & Soaps": {
        "business_name": "Glow Essence Botanicals",
        "category": "Beauty & Skincare",
        "product_name": "Radiance Facial Cream & Artisan Glow Soaps",
        "description": "Natural organic facial cream and raw African black soap bars formulated to nourish skin, clear blemishes, and restore radiance.",
        "target_audience": "Individuals desiring radiant, even-toned, healthy skin",
        "selling_points": "All-natural ingredients, cruelty-free, noticeable results in 14 days",
        "tone": "Premium & Luxurious",
        "aspect_ratio": "9:16",
        "duration": 15,
        "call_to_action": "Shop the glow routine online today!"
    }
}

# -------------------------------------------------------------
# THEME INJECTION & STYLES
# -------------------------------------------------------------
css_path = PROJECT_ROOT / "assets" / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

active_theme_class = f"theme-{st.session_state.theme.replace('_', '-')}"
st.markdown(f'<div class="{active_theme_class}"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR: THEME SWITCHER & API CONFIGURATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎨 Appearance & Theme")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🌙 Dark Blue", use_container_width=True, 
                     type="primary" if st.session_state.theme == "dark_blue" else "secondary"):
            st.session_state.theme = "dark_blue"
            st.rerun()
            
    with col_t2:
        if st.button("☀️ Clean White", use_container_width=True,
                     type="primary" if st.session_state.theme == "clean_white" else "secondary"):
            st.session_state.theme = "clean_white"
            st.rerun()

    current_theme_label = "Deep Midnight Navy & Cyan" if st.session_state.theme == "dark_blue" else "Clean White & Slate Blue"
    st.caption(f"Active Theme: **{current_theme_label}**")
    
    st.divider()

    st.markdown("### ⚡ Generation Speed")
    st.success("⚡ **Ultra-Fast Mode Active:** Videos render in 3–8 seconds using high-speed scene flattening.")

    st.divider()

    st.markdown("### 🔑 API Integrations")
    st.markdown(
        "<small style='opacity:0.8;'>Set in <code>.env</code> or enter below for your session.</small>",
        unsafe_allow_html=True
    )

    env_gemini = get_gemini_api_key()
    env_pexels = get_pexels_api_key()
    env_eleven = get_elevenlabs_api_key()

    gemini_key = st.text_input(
        "Google Gemini API Key",
        value=st.session_state.get("sidebar_gemini", env_gemini),
        type="password",
        help="Used to generate compelling marketing scripts using Gemini models.",
        key="sidebar_gemini"
    )

    pexels_key = st.text_input(
        "Pexels API Key",
        value=st.session_state.get("sidebar_pexels", env_pexels),
        type="password",
        help="Used to retrieve relevant stock videos and photographs.",
        key="sidebar_pexels"
    )

    eleven_key = st.text_input(
        "ElevenLabs API Key (Optional)",
        value=st.session_state.get("sidebar_eleven", env_eleven),
        type="password",
        help="Optional: For studio-quality AI voices. Falls back to gTTS if empty.",
        key="sidebar_eleven"
    )

    st.markdown("#### Visuals & Voice Status")
    
    if st.session_state.get("user_product_photos"):
        st.markdown(f"🟢 **Visuals:** {len(st.session_state.user_product_photos)} Custom Product Photos Uploaded")
    elif pexels_key:
        st.markdown("🟢 **Visuals:** Pexels Stock Media + Product Catalog")
    else:
        st.markdown("🟢 **Visuals:** Real Commercial Product Photos (Bundled)")

    if eleven_key:
        st.markdown("🟢 **Voiceover:** ElevenLabs Neural Voice")
    else:
        st.markdown("🟢 **Voiceover:** Google Text-to-Speech (Instant & Free)")

    st.divider()
    st.markdown("#### 💡 Cost & Transparency")
    st.caption(
        "• **100% Free & Fast:** Generates promotional videos using your uploaded photos or commercial product catalog, gTTS voiceover, and smart commercial copy.\n"
        "• **Live AI Mode:** Add Gemini and Pexels keys for live custom text and stock footage."
    )

# -------------------------------------------------------------
# MAIN HEADER & STEPPER
# -------------------------------------------------------------
st.markdown(f"""
<div class="hero-container">
    <div class="hero-tag">✨ AI Promotional Video Studio for Small Businesses</div>
    <div class="hero-title">AI Video Generator for Small Businesses</div>
    <div class="hero-subtitle">
        Create professional promotional videos with actual product pictures in seconds.
        Upload your product photos, generate high-converting marketing scripts, and render ready-to-post MP4 videos.
    </div>
</div>
""", unsafe_allow_html=True)

# Visual Workflow Stepper
step = st.session_state.current_step
st.markdown(f"""
<div class="stepper-container">
    <div class="step-card {'active' if step == 1 else 'inactive'}">
        <div class="step-number">1</div>
        <div class="step-text">Describe & Upload Product</div>
    </div>
    <div class="step-card {'active' if step == 2 else 'inactive'}">
        <div class="step-number">2</div>
        <div class="step-text">Review Script</div>
    </div>
    <div class="step-card {'active' if step == 3 else 'inactive'}">
        <div class="step-number">3</div>
        <div class="step-text">Fast Video Assembly</div>
    </div>
    <div class="step-card {'active' if step == 4 else 'inactive'}">
        <div class="step-number">4</div>
        <div class="step-text">Preview & Download</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# STEP 1: BUSINESS & PRODUCT CREATION WORKSPACE
# -------------------------------------------------------------
if st.session_state.current_step == 1:
    st.markdown("### Step 1: Tell Us About Your Business & Product")
    st.write("Fill in your product details and upload product pictures, or click an example preset below:")

    # Preset templates
    sample_col1, sample_col2, sample_col3 = st.columns([1, 1, 1])
    for i, (sample_name, sample_vals) in enumerate(SAMPLE_BUSINESSES.items()):
        col = [sample_col1, sample_col2, sample_col3][i]
        with col:
            if st.button(f"Load {sample_name}", use_container_width=True):
                st.session_state.business_data.update(sample_vals)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("business_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input(
                "Business Name *",
                value=st.session_state.business_data.get("business_name", ""),
                placeholder="e.g. Bella Chic Boutique",
                help="Your brand or store name as customers know it."
            )
            
            category = st.selectbox(
                "Business Category *",
                options=BUSINESS_CATEGORIES,
                index=BUSINESS_CATEGORIES.index(st.session_state.business_data.get("category", BUSINESS_CATEGORIES[0]))
                if st.session_state.business_data.get("category") in BUSINESS_CATEGORIES else 0
            )

            product_name = st.text_input(
                "Product or Service Name *",
                value=st.session_state.business_data.get("product_name", ""),
                placeholder="e.g. Ankara Wrap Dress, Jollof Rice, or Facial Glow Cream"
            )

            description = st.text_area(
                "Product or Service Description *",
                value=st.session_state.business_data.get("description", ""),
                height=100,
                placeholder="Describe what you are selling, its main features, and why customers love it."
            )

        with col2:
            target_audience = st.text_input(
                "Target Audience",
                value=st.session_state.business_data.get("target_audience", ""),
                placeholder="e.g. Working women, students, foodies in Lagos"
            )

            selling_points = st.text_input(
                "Key Selling Points / Special Offers",
                value=st.session_state.business_data.get("selling_points", ""),
                placeholder="e.g. 100% organic, 20% discount this week, free delivery"
            )

            tone = st.selectbox(
                "Preferred Marketing Tone",
                options=MARKETING_TONES,
                index=MARKETING_TONES.index(st.session_state.business_data.get("tone", MARKETING_TONES[0]))
                if st.session_state.business_data.get("tone") in MARKETING_TONES else 0
            )

            col_ar, col_dur = st.columns(2)
            with col_ar:
                ar_labels = {k: v["label"] for k, v in ASPECT_RATIOS.items()}
                current_ar = st.session_state.business_data.get("aspect_ratio", "9:16")
                ar_keys = list(ASPECT_RATIOS.keys())
                ar_idx = ar_keys.index(current_ar) if current_ar in ar_keys else 0
                
                selected_ar = st.selectbox(
                    "Video Format / Aspect Ratio",
                    options=ar_keys,
                    format_func=lambda x: ar_labels[x],
                    index=ar_idx
                )

            with col_dur:
                current_dur = st.session_state.business_data.get("duration", 15)
                dur_idx = SUPPORTED_DURATIONS.index(current_dur) if current_dur in SUPPORTED_DURATIONS else 0
                selected_dur = st.selectbox(
                    "Target Duration",
                    options=SUPPORTED_DURATIONS,
                    format_func=lambda x: f"{x} Seconds",
                    index=dur_idx
                )

        col_cta, col_music = st.columns([3, 1])
        with col_cta:
            call_to_action = st.text_input(
                "Call to Action (Optional)",
                value=st.session_state.business_data.get("call_to_action", "Call or WhatsApp us today to order!"),
                placeholder="e.g. Click link in bio or WhatsApp +234..."
            )
        with col_music:
            include_bg_music = st.checkbox(
                "Background Music",
                value=st.session_state.business_data.get("include_bg_music", True),
                help="Adds gentle ambient background music under the voiceover."
            )

        st.markdown("---")
        st.markdown("#### 📸 Upload Your Real Product Photos *(Optional)*")
        st.caption(
            "Want your actual product displayed on the video? Upload 1 to 5 photos of your dresses, meals, creams, soaps, or items. "
            "If left empty, the AI will automatically showcase real commercial product photography tailored to your category."
        )

        uploaded_files = st.file_uploader(
            "Select product photos (JPG, PNG, WebP):",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="product_pic_uploader"
        )

        submit_form = st.form_submit_button("Generate Marketing Script ➔", type="primary", use_container_width=True)

        if submit_form:
            # Process uploaded images
            user_uploaded_paths = []
            if uploaded_files:
                upload_dir = PROJECT_ROOT / "temp" / "user_uploads"
                upload_dir.mkdir(parents=True, exist_ok=True)
                for uf in uploaded_files:
                    save_dest = upload_dir / f"upload_{uuid.uuid4().hex[:6]}_{uf.name}"
                    with open(save_dest, "wb") as f:
                        f.write(uf.getbuffer())
                    user_uploaded_paths.append(str(save_dest))
                st.session_state.user_product_photos = user_uploaded_paths

            # Update session state
            st.session_state.business_data = {
                "business_name": business_name,
                "category": category,
                "product_name": product_name,
                "description": description,
                "target_audience": target_audience,
                "selling_points": selling_points,
                "tone": tone,
                "aspect_ratio": selected_ar,
                "duration": selected_dur,
                "call_to_action": call_to_action,
                "include_bg_music": include_bg_music
            }

            # Validate
            is_valid, validation_errors = validate_business_inputs(st.session_state.business_data)
            if not is_valid:
                for err in validation_errors:
                    st.error(f"⚠️ {err}")
            else:
                with st.spinner("Writing customized marketing script with AI..."):
                    script_info = generate_marketing_script(
                        st.session_state.business_data,
                        api_key=gemini_key
                    )
                    st.session_state.script_result = script_info
                    st.session_state.confirmed_script = script_info.get("narration", "")
                    st.session_state.current_step = 2
                    st.rerun()

    # Visual Preview of Selected Product Pictures
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.get("user_product_photos"):
        st.markdown("#### 🖼️ Your Active Product Photos:")
        cols = st.columns(min(5, len(st.session_state.user_product_photos)))
        for i, upath in enumerate(st.session_state.user_product_photos[:5]):
            with cols[i]:
                st.image(upath, caption=f"Your Product {i+1}", use_container_width=True)
    else:
        current_cat = st.session_state.business_data.get("category", "Fashion & Apparel")
        sample_pics = get_bundled_product_photos(current_cat)
        if sample_pics:
            st.markdown(f"#### 🖼️ Automatic Commercial Product Photos for *{current_cat}*:")
            cols = st.columns(min(4, len(sample_pics)))
            for i, spath in enumerate(sample_pics[:4]):
                with cols[i]:
                    st.image(spath, caption=f"Product Visual {i+1}", use_container_width=True)

# -------------------------------------------------------------
# STEP 2: SCRIPT REVIEW & EDIT WORKSPACE
# -------------------------------------------------------------
elif st.session_state.current_step == 2:
    st.markdown("### Step 2: Review and Refine Your Marketing Script")
    st.write("Review the generated promotional narration. You can edit the text directly to match your voice.")

    if st.session_state.script_result and "warning" in st.session_state.script_result:
        st.info(f"ℹ️ {st.session_state.script_result['warning']}")

    edited_script = st.text_area(
        "Voiceover Narration Script (Editable):",
        value=st.session_state.confirmed_script,
        height=180,
        help="This text will be converted into spoken voiceover audio."
    )
    
    st.session_state.confirmed_script = edited_script

    # Stats and Overlay tags
    words = len(edited_script.split())
    approx_time = round(words / 2.3, 1)
    target_d = st.session_state.business_data.get("duration", 15)

    col_meta1, col_meta2 = st.columns([1, 2])
    with col_meta1:
        st.markdown(f"**Word Count:** {words} words (~{approx_time}s speaking time)")
        if approx_time > target_d + 5:
            st.warning(f"⚠️ Script might be slightly long for a {target_d}s video. We will adjust video length to fit.")
    
    with col_meta2:
        overlays = st.session_state.script_result.get("overlays", []) if st.session_state.script_result else []
        if overlays:
            st.markdown("**Key On-Screen Captions:** " + " • ".join([f"`{o}`" for o in overlays]))

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("⬅️ Back to Business Details", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()

    with col_btn2:
        if st.button("🔄 Regenerate Script", use_container_width=True):
            with st.spinner("Regenerating script with AI..."):
                script_info = generate_marketing_script(
                    st.session_state.business_data,
                    api_key=gemini_key
                )
                st.session_state.script_result = script_info
                st.session_state.confirmed_script = script_info.get("narration", "")
                st.rerun()

    with col_btn3:
        if st.button("Confirm Script & Continue ➔", type="primary", use_container_width=True):
            is_valid, script_errors = validate_script(st.session_state.confirmed_script, target_duration=target_d)
            if not is_valid:
                for err in script_errors:
                    st.error(f"⚠️ {err}")
            else:
                st.session_state.current_step = 3
                st.rerun()

# -------------------------------------------------------------
# STEP 3: VIDEO GENERATION WORKSPACE (HIGH-SPEED ENGINE)
# -------------------------------------------------------------
elif st.session_state.current_step == 3:
    st.markdown("### Step 3: Fast Video Assembly")
    st.write("Ready to build your promotional video! The optimized engine renders your MP4 in seconds.")

    b = st.session_state.business_data
    user_imgs = st.session_state.get("user_product_photos", [])
    
    st.markdown(f"""
    <div class="custom-card">
        <h4 style="margin-top:0;">Production Plan</h4>
        <p><strong>Business:</strong> {b.get('business_name')} ({b.get('category')})</p>
        <p><strong>Product:</strong> {b.get('product_name')}</p>
        <p><strong>Format:</strong> {ASPECT_RATIOS.get(b.get('aspect_ratio', '9:16'), {}).get('label')} | <strong>Target Duration:</strong> {b.get('duration')}s</p>
        <p><strong>Product Visuals:</strong> {'Using ' + str(len(user_imgs)) + ' uploaded product photos' if user_imgs else 'Using authentic commercial product photos for ' + b.get('category')}</p>
        <p><strong>Script Preview:</strong> <em>"{st.session_state.confirmed_script[:120]}..."</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Gallery preview of photos that will appear in the video
    if user_imgs:
        st.markdown("##### 📸 Photos Appearing in Video (Your Uploaded Products):")
        cols = st.columns(min(4, len(user_imgs)))
        for i, upath in enumerate(user_imgs[:4]):
            with cols[i]:
                st.image(upath, caption=f"Product Scene {i+1}", use_container_width=True)
    else:
        sample_pics = get_bundled_product_photos(b.get("category", "Fashion & Apparel"))
        if sample_pics:
            st.markdown(f"##### 📸 Real Product Photos Appearing in Video:")
            cols = st.columns(min(4, len(sample_pics)))
            for i, spath in enumerate(sample_pics[:4]):
                with cols[i]:
                    st.image(spath, caption=f"Product Scene {i+1}", use_container_width=True)

    col_back, col_gen = st.columns([1, 2])
    with col_back:
        if st.button("⬅️ Edit Script", use_container_width=True, disabled=st.session_state.is_processing):
            st.session_state.current_step = 2
            st.rerun()

    with col_gen:
        generate_clicked = st.button(
            "⚡ Generate My Video Now",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.is_processing
        )

    if generate_clicked:
        st.session_state.is_processing = True
        
        status_box = st.status("🚀 Producing your promotional video...", expanded=True)
        progress_bar = st.progress(0.0)

        try:
            # 1. Voiceover Generation
            status_box.write("🎙️ **Step 1/3:** Generating voiceover audio narration...")
            progress_bar.progress(0.25)
            
            voice_result = generate_voiceover(
                script_text=st.session_state.confirmed_script,
                api_key=eleven_key
            )
            status_box.write(f"✓ Voiceover complete using **{voice_result['provider'].upper()}** ({voice_result['duration']:.1f}s)")
            progress_bar.progress(0.50)

            # 2. Real Product Media Retrieval
            status_box.write("🖼️ **Step 2/3:** Loading real product photos and visual scenes...")
            keywords = st.session_state.script_result.get("search_keywords", []) if st.session_state.script_result else []
            if not keywords:
                keywords = [b.get("product_name"), b.get("category")]

            media_assets = fetch_media_assets(
                keywords=keywords,
                category=b.get("category", "General"),
                aspect_ratio=b.get("aspect_ratio", "9:16"),
                num_scenes=3,
                api_key=pexels_key,
                user_uploaded_images=st.session_state.get("user_product_photos", [])
            )
            media_sources = [m["source"] for m in media_assets]
            status_box.write(f"✓ Prepared {len(media_assets)} real product visual scenes ({', '.join(set(media_sources))})")
            progress_bar.progress(0.70)

            # 3. High-Speed Video Composition
            status_box.write("⚙️ **Step 3/3:** Rapid compositing and high-speed MP4 encoding...")
            
            overlays = st.session_state.script_result.get("overlays", []) if st.session_state.script_result else []
            if not overlays:
                overlays = [b.get("product_name"), "Premium Quality", b.get("call_to_action", "Order Today!")]

            def update_composition_progress(msg, pct):
                overall = 0.70 + pct * 0.28
                progress_bar.progress(min(0.98, overall))
                status_box.write(f"• {msg}")

            composition_result = compose_promotional_video(
                media_assets=media_assets,
                voiceover_path=voice_result["audio_path"],
                voiceover_duration=voice_result["duration"],
                overlays=overlays,
                business_name=b.get("business_name", ""),
                aspect_ratio=b.get("aspect_ratio", "9:16"),
                target_duration=b.get("duration", 15),
                include_bg_music=b.get("include_bg_music", True),
                progress_callback=update_composition_progress
            )

            progress_bar.progress(1.0)
            status_box.update(label="🎉 Video generated successfully in seconds!", state="complete", expanded=False)

            st.session_state.generated_video = composition_result
            st.session_state.is_processing = False
            st.session_state.current_step = 4
            st.rerun()

        except Exception as e:
            st.session_state.is_processing = False
            status_box.update(label="❌ Generation failed", state="error", expanded=True)
            st.error(f"Video generation encountered an error: {str(e)}")

# -------------------------------------------------------------
# STEP 4: VIDEO PREVIEW & DOWNLOAD WORKSPACE
# -------------------------------------------------------------
elif st.session_state.current_step == 4:
    st.markdown("### Step 4: Preview and Download Your Video")
    st.write("Your promotional video with your actual product pictures has been rendered and is ready for social media.")

    video_data = st.session_state.generated_video
    if not video_data or not Path(video_data["video_path"]).exists():
        st.error("Generated video file was not found. Please re-run the generation step.")
        if st.button("⬅️ Return to Assembly"):
            st.session_state.current_step = 3
            st.rerun()
    else:
        video_path = video_data["video_path"]
        
        # Display Video Stats
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-pill">
                <div class="stat-label">Duration</div>
                <div class="stat-value">{video_data['duration']}s</div>
            </div>
            <div class="stat-pill">
                <div class="stat-label">Aspect Ratio</div>
                <div class="stat-value">{video_data['aspect_ratio']}</div>
            </div>
            <div class="stat-pill">
                <div class="stat-label">Resolution</div>
                <div class="stat-value">{video_data['resolution']}</div>
            </div>
            <div class="stat-pill">
                <div class="stat-label">File Size</div>
                <div class="stat-value">{video_data['file_size_mb']} MB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_player, col_actions = st.columns([1.2, 1])

        with col_player:
            st.video(video_path)

        with col_actions:
            st.markdown("#### Export & Sharing")
            st.write("Post your video on WhatsApp Status, Instagram Reels, TikTok, YouTube Shorts, or Facebook.")

            with open(video_path, "rb") as vf:
                video_bytes = vf.read()

            st.download_button(
                label="⬇️ Download Promotional Video (MP4)",
                data=video_bytes,
                file_name=video_data["filename"],
                mime="video/mp4",
                type="primary",
                use_container_width=True
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Create Another Video", use_container_width=True):
                st.session_state.generated_video = None
                st.session_state.script_result = None
                st.session_state.confirmed_script = ""
                st.session_state.user_product_photos = []
                st.session_state.current_step = 1
                st.rerun()

            if st.button("🔄 Adjust Details or Pictures", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
