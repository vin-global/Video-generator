# AI Video Generator for Small Businesses

An automated, web-based AI digital marketing video generation system designed specifically for small business owners and local entrepreneurs. The system enables users to create professional, ready-to-post promotional videos in minutes—without requiring prior video editing skills, large marketing budgets, or expensive production software.

---

## 🌟 Key Features

1. **AI Commercial Scriptwriting (Google Gemini API):**
   - Automatically generates targeted, persuasive commercial scripts based on the user's business category, target audience, marketing tone, and key selling points.
   - Paces narration to comfortably match video duration (~2.2 words per second).
   - Extracts on-screen caption phrases and visual search keywords.
   - Includes smart offline business templates for keyless/offline testing.

2. **Automated Voiceover Narration:**
   - Supports **ElevenLabs API** for studio-grade neural voices.
   - Built-in automatic fallback to **Google Text-to-Speech (gTTS)**, guaranteeing reliable voiceover generation without mandatory subscription costs.

3. **Contextual Stock Media Retrieval:**
   - Searches and downloads high-definition videos and photos from **Pexels API** matching the business category and aspect ratio.
   - Built-in **Illustrative Visual Generator** powered by Pillow that crafts modern, high-resolution gradient canvas scenes when API keys are absent or stock media is unavailable.

4. **Professional Video Composition Engine (MoviePy + Pillow):**
   - Produces real, downloadable `.mp4` video files with H.264 video and AAC audio codecs.
   - Supports 3 standard social formats:
     - **9:16 (Vertical)**: TikTok, Instagram Reels, YouTube Shorts.
     - **1:1 (Square)**: Instagram & Facebook feed posts.
     - **16:9 (Landscape)**: YouTube, websites, and displays.
   - Centers and crops media without distortion.
   - Renders anti-aliased, frosted-glass text overlays, synchronized lower-third caption pills, and a branded header badge.
   - Audio mixing with gentle ambient background music and automatic voice ducking.

5. **Customized UI with Dual-Theme Switcher:**
   - **🌙 Dark Blue Theme:** Deep midnight navy gradients (`#060D1F`), glowing cyan accents (`#38BDF8`), and frosted glass cards.
   - **☀️ Clean White Theme:** Minimalist crisp white canvas (`#FFFFFF`), slate blue accents (`#2563EB`), and subtle soft drop shadows.
   - One-click instant theme toggle in both header and sidebar.

6. **Full-Cycle 4-Step Guided Workflow:**
   - **Step 1:** Describe Business & Product (with quick-load presets).
   - **Step 2:** Review & Refine Generated Marketing Script.
   - **Step 3:** Automated Video Assembly with live progress tracking.
   - **Step 4:** Playable Preview, Output Metrics, and Direct MP4 Download.

---

## 🏗️ Architecture & Project Structure

```
VIDEO/
├── app.py                      # Main Streamlit web application entrypoint
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable configuration template
├── .gitignore                  # Git ignore rules (secrets, venv, temporary media)
├── README.md                   # Complete documentation
│
├── modules/
│   ├── __init__.py
│   ├── config.py               # Constants, dimensions, paths, and API key loading
│   ├── validators.py           # Comprehensive input validation
│   ├── script_generator.py     # Gemini AI script generator + smart fallback templates
│   ├── voice_generator.py      # ElevenLabs & gTTS audio narration generator
│   ├── media_fetcher.py        # Pexels API retriever + illustrative scene generator
│   └── video_composer.py       # MoviePy composition, Pillow overlays, and MP4 renderer
│
├── assets/
│   ├── music/
│   │   └── ambient_gentle.wav  # Self-contained royalty-free background loop
│   └── styles.css              # Custom responsive stylesheet (Dark Blue & Clean White)
│
├── temp/                       # Scratch processing directory for temporary audio/clips
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    ├── test_validators.py       # Input validation tests
    ├── test_script_generator.py # Template & Gemini script tests
    ├── test_voice_generator.py  # gTTS & ElevenLabs voice tests
    ├── test_media_fetcher.py    # Media retrieval & illustrative scene tests
    ├── test_video_composer.py   # MoviePy MP4 render integration test
    └── test_app_workflow.py     # Streamlit AppTest UI & theme toggle verification
```

---

## ⚙️ Prerequisites & Installation

### 1. Python Environment
Python **3.10** or **3.11** is recommended.

Clone or open the project folder in your terminal:
```bash
cd c:\Users\user\Documents\PROJECTS\VIDEO
```

Create and activate a virtual environment:
```bash
# Using Python venv
python -m venv .venv
.venv\Scripts\activate       # On Windows
# source .venv/bin/activate  # On Linux/macOS
```

Or using `uv` (fast package manager):
```bash
uv venv .venv --python 3.11
.venv\Scripts\activate
```

### 2. Install Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

*Note on FFmpeg:* FFmpeg is automatically provided and managed via `imageio-ffmpeg` which bundles a standalone static FFmpeg binary. No separate system-level FFmpeg installation is required!

---

## 🔑 Configuration & API Keys

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Configure your credentials in `.env`:
```env
# Google Gemini API Key (Required for AI script generation)
# Get a free key at: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# Pexels API Key (Required for stock videos and photos)
# Get a free key at: https://www.pexels.com/api/
PEXELS_API_KEY=your_pexels_api_key_here

# ElevenLabs API Key (Optional: for premium AI voiceovers)
# Get key at: https://elevenlabs.io/
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

> **Zero-Configuration Mode:** You can run the application **immediately without any API keys**. The system will automatically use intelligent business fallback templates for scriptwriting, Google Text-to-Speech (gTTS) for voiceovers, and branded illustrative graphics for visuals.

---

## 🚀 Running the Application

To launch the web interface, run:
```bash
streamlit run app.py
```

Or when running from the virtual environment:
```bash
.venv\Scripts\streamlit.exe run app.py
```

Once running, open your web browser at:
`http://localhost:8501`

---

## 🧪 Running the Automated Test Suite

The test suite covers unit tests, mocked API integrations, end-to-end MP4 video composition, and Streamlit UI testing.

To run all 17 tests:
```bash
.venv\Scripts\pytest -v -p no:cacheprovider
```

Example test output:
```
tests/test_app_workflow.py::test_app_initial_load_and_theme_toggle PASSED
tests/test_app_workflow.py::test_app_form_submission_to_step_2 PASSED
tests/test_media_fetcher.py::test_generate_illustrative_scene PASSED
tests/test_media_fetcher.py::test_fetch_media_assets_fallback PASSED
tests/test_media_fetcher.py::test_search_pexels_photos_mock PASSED
tests/test_script_generator.py::test_generate_fallback_script PASSED
tests/test_script_generator.py::test_generate_marketing_script_without_key PASSED
tests/test_script_generator.py::test_generate_marketing_script_with_mocked_gemini PASSED
tests/test_validators.py::test_validate_business_inputs_valid PASSED
tests/test_validators.py::test_validate_business_inputs_missing_fields PASSED
tests/test_validators.py::test_validate_script_valid PASSED
tests/test_validators.py::test_validate_script_empty_or_too_short PASSED
tests/test_video_composer.py::test_create_text_overlay_image PASSED
tests/test_video_composer.py::test_compose_promotional_video_end_to_end PASSED
tests/test_voice_generator.py::test_generate_voiceover_gtts_creates_file PASSED
tests/test_voice_generator.py::test_generate_voiceover_empty_text PASSED
tests/test_voice_generator.py::test_generate_voiceover_elevenlabs_mock PASSED

======================= 17 passed in 226.23s =======================
```

---

## 🛠️ Common Errors & Troubleshooting

1. **`AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'`**
   - *Cause:* Pillow 10+ removed `Image.ANTIALIAS` in favor of `Image.Resampling.LANCZOS`.
   - *Solution:* Handled automatically in `modules/video_composer.py` with the compatibility patch `PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS`.

2. **`PermissionError: [WinError 5] Access is denied` during video rendering**
   - *Cause:* Windows file locking on temporary audio streams when closing FFmpeg processes.
   - *Solution:* `modules/video_composer.py` writes to a dedicated temporary audio path with `remove_temp=False` and cleanly unlinks the file in a `finally` block after closing all clip handles.

3. **`GEMINI_API_KEY` missing or Quota Exceeded**
   - *Solution:* The app automatically falls back to smart business templates, alerting the user in the UI without halting the workflow.

4. **Pexels Rate Limit or No Results Found**
   - *Solution:* The application seamlessly generates high-resolution, category-themed illustrative scenes with modern gradient canvases so video generation always succeeds.

---

## 🚢 Deployment Considerations

- **Memory Allocation:** Video rendering creates image frames in RAM. A minimum of 2 GB RAM (4 GB recommended) is advised for hosting on Cloud Run, Render, Railway, or AWS EC2.
- **CPU:** FFmpeg video encoding utilizes multiple CPU threads. For fast rendering (under 30s), a 2-vCPU or 4-vCPU instance is optimal.
- **Disk Space:** Ensure at least 1 GB of temporary disk space is available for video processing. The application stores active renders in `temp/` which can be cleared periodically.
- **Stateless Operation:** The application does not require a persistent database or user logins, making it easy to deploy as a containerized Docker service or serverless container.

---

## 📜 License & Acknowledgments

Developed as an applied project for small business digital enablement in emerging markets. 
Media assets retrieved via Pexels API comply with Pexels License terms. Voiceovers powered by ElevenLabs & Google Text-to-Speech. Scripts powered by Google Gemini.
