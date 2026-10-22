"""Streamlit AppTest automated UI and workflow verification."""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).parent.parent / "app.py"

def test_app_initial_load_and_theme_toggle():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    assert not at.exception
    
    # Check default theme is dark_blue
    assert at.session_state["theme"] == "dark_blue"
    assert at.session_state["current_step"] == 1

    # Find the "☀️ Clean White" theme button and click it
    clean_white_btn = None
    for btn in at.button:
        if "Clean White" in btn.label:
            clean_white_btn = btn
            break
            
    assert clean_white_btn is not None
    clean_white_btn.click().run()
    assert not at.exception
    assert at.session_state["theme"] == "clean_white"

    # Now click the "🌙 Dark Blue" button to switch back
    dark_blue_btn = None
    for btn in at.button:
        if "Dark Blue" in btn.label:
            dark_blue_btn = btn
            break

    assert dark_blue_btn is not None
    dark_blue_btn.click().run()
    assert not at.exception
    assert at.session_state["theme"] == "dark_blue"

def test_app_form_submission_to_step_2():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    assert not at.exception

    # Submit the business creation form
    form_submit = None
    for btn in at.button:
        if "Generate Marketing Script" in btn.label:
            form_submit = btn
            break

    assert form_submit is not None
    form_submit.click().run()
    assert not at.exception

    # Verify workflow transitioned to Step 2
    assert at.session_state["current_step"] == 2
    assert len(at.session_state["confirmed_script"]) > 10

def test_app_form_submission_with_uploaded_image(tmp_path):
    # Create a small dummy test image
    test_img = tmp_path / "test_product.jpg"
    from PIL import Image
    im = Image.new("RGB", (100, 100), color="red")
    im.save(test_img, format="JPEG")

    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    assert not at.exception

    # Upload test image to the file uploader
    if len(at.file_uploader) > 0:
        uploader = at.file_uploader[0]
        # streamlit AppTest supports .upload() with bytes/files
        with open(test_img, "rb") as f:
            uploader.files = [test_img]
            
    # Submit the business creation form
    form_submit = None
    for btn in at.button:
        if "Generate Marketing Script" in btn.label:
            form_submit = btn
            break

    assert form_submit is not None
    form_submit.click().run()
    assert not at.exception
    assert at.session_state["current_step"] == 2

