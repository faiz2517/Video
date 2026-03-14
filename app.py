# app.py
import streamlit as st
import os
import base64
import time
import requests
from dotenv import load_dotenv
from PIL import Image
import xai_sdk

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="grok-ugc-ad-video-maker",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🎥 Grok UGC Ad Video Maker")
st.markdown("**Turn any product photo into a 10-second viral UGC ad** using xAI's official **grok-imagine-video** model (March 2026). Powered by Grok Imagine Video API.")

# API Key check
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    st.error("⚠️ XAI_API_KEY not found in .env. Get it from https://console.x.ai → API Keys.")
    st.stop()

client = xai_sdk.Client(api_key=XAI_API_KEY)

# Sidebar inputs
with st.sidebar:
    st.header("🎯 Campaign Settings")
    
    audience = st.text_input(
        "Target Audience",
        value="18-30 Indian girls",
        help="Describe age, demographics, style, ethnicity for relatable talent"
    )
    
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        options=["9:16", "16:9", "1:1"],
        index=0,
        help="9:16 = Vertical (Reels/TikTok/Shorts), 16:9 = Horizontal, 1:1 = Square"
    )
    
    platform = st.selectbox(
        "Target Platform",
        options=["Instagram Reels", "TikTok", "YouTube Shorts"],
        index=0
    )
    
    st.markdown("---")
    st.caption("💰 \~$0.70 per 10-second 720p video (billed \~$0.07/sec + image input). URLs temporary — download immediately!")

# Main area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Upload Product Image")
    uploaded_file = st.file_uploader(
        "Choose a clear, well-lit product photo (JPEG/PNG recommended)",
        type=["jpg", "jpeg", "png"],
        help="Best results: centered product, plain or natural background"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Product", use_column_width=True)
        
        # Convert to data URI
        bytes_data = uploaded_file.getvalue()
        b64 = base64.b64encode(bytes_data).decode("utf-8")
        file_ext = uploaded_file.name.split(".")[-1].lower()
        mime_type = "jpeg" if file_ext in ["jpg", "jpeg"] else file_ext
        data_uri = f"data:image/{mime_type};base64,{b64}"

with col2:
    if uploaded_file:
        st.subheader("🚀 Generate UGC Ad")
        if st.button("Generate 10-Second Ad Video", type="primary", use_container_width=True):
            status = st.status("Starting generation...", expanded=True)
            
            try:
                status.update(label="Crafting detailed prompt...", state="running")
                
                # Ultra-detailed prompt — keeps product 100% consistent, UGC style
                prompt = f"""
Create a natural, authentic 10-second UGC-style advertisement video, exactly like real iPhone-shot TikTok/Reels content.

Begin with the exact uploaded product as the main focus.
Feature a relatable, energetic {audience} person (accurate age, ethnicity, fashion, vibe) who excitedly finds and uses the product in real-life setting — turning it on, showing key features naturally (e.g. breeze/hair movement if fan-like, portability demo), big genuine smile, happy surprised reaction.

**EXTREMELY STRICT PRODUCT CONSISTENCY**: The product MUST remain 100% identical in EVERY single frame to the input image — exact shape, colors, logos, text, textures, reflections, proportions. No changes, no AI hallucinations or variations on the product at all.

Camera work: casual handheld UGC style — slight natural shake, dynamic close-ups to medium shots, vibrant everyday lighting.

Background audio: upbeat chill lo-fi music + realistic SFX (clicks, happy reactions, subtle environment sounds). No voiceover.

Pacing optimized for {platform}: hook in first 2-3 seconds, build excitement, strong emotional close.

In the last 3-4 seconds, overlay clean modern text (bold white font, soft shadow/outline):
"Only ₹299 🌸 Shop Now"

10 seconds exactly, 720p cinematic quality, high-energy yet super relatable UGC feel.
"""

                status.update(label="Submitting to Grok Imagine Video API (30–90s)...", state="running")
                
                response = client.video.generate(
                    prompt=prompt.strip(),
                    model="grok-imagine-video",
                    image_url=data_uri,
                    duration=10,
                    aspect_ratio=aspect_ratio,
                    resolution="720p"
                )

                video_url = response.url
                actual_duration = getattr(response, 'duration', 10)  # fallback

                status.update(label=f"✅ Video ready! ({actual_duration}s)", state="complete")
                st.success(f"Video generated successfully! ({actual_duration}s)")

                st.video(video_url)

                video_bytes = requests.get(video_url).content
                st.download_button(
                    label="📥 Download MP4 Now",
                    data=video_bytes,
                    file_name=f"ugc_ad_{platform.replace(' ', '_')}_{int(time.time())}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

                st.caption("⚠️ Video URL expires soon — download right away!")

            except xai_sdk.exceptions.APIError as e:  # adjust exception name if needed after pip install -U
                status.update(label="Error occurred", state="error")
                err_str = str(e).lower()
                if "credit" in err_str or "balance" in err_str:
                    st.error("API credits / balance issue. Check & top up at https://console.x.ai")
                elif "duration" in err_str:
                    st.warning("Duration issue — API max is 15s but try 8s if persistent problems.")
                elif "image" in err_str or "url" in err_str:
                    st.error("Image processing failed. Try a different/clearer photo.")
                else:
                    st.error(f"API error: {str(e)}\nTip: Update xai-sdk (`pip install -U xai-sdk`) and retry.")

            except Exception as e:
                status.update(label="Unexpected error", state="error")
                st.error(f"Something went wrong: {str(e)}\nMake sure xai-sdk is up to date.")

    else:
        st.info("👆 Upload your product image to start generating!")

# Footer
st.markdown("---")
st.markdown(
    "Built with Streamlit + official xAI SDK (March 2026). "
    "Deploy free → Streamlit Cloud / Hugging Face Spaces. "
    "Star on GitHub if useful!"
)
