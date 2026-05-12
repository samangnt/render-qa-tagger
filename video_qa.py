import os
import io
from google import generativeai as genai
import pandas as pd
import streamlit as st
import json
import datetime
import pypdf
import tempfile
import cv2

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# All available models in priority order
MODELS = [
    'gemini-3.0-flash',
    'gemini-2.5-flash',
    'gemini-3.0-flash-lite',
    'gemini-2.5-flash-lite'
]


# Development mode — uses only one model
DEV_MODE = True
#this selects the ai model then reads image_part from popping a frame from video frame by frame
def get_ai_response(prompt, image_part):
    
    # Development — single model only
    if DEV_MODE:
        model = genai.GenerativeModel(MODELS[2])  # safest/cheapest
        return model.generate_content([prompt, image_part])
    
    # Production — fallback chain
    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image_part])
            st.caption(f"⚡ Powered by {model_name}")
            return response
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue  # try next model
            else:
                raise e  # real error, don't retry
    
    raise Exception("All models exhausted. Try again tomorrow.")


#title and line
st.set_page_config(layout='wide')
st.title("🎥 Video QA Auto-Tagger")
st.write("Upload your 3D render video to automatically tag and critique it against your script.")

#1. video Uploader
uploaded_video = st.file_uploader(
    "Upload Video (Max 1080p, 30fps, 1min)", 
    type=["mp4", "mov", "avi", "webm", "wmv"]
)

#2. Script uploader with text area
tab1, tab2 = st.tabs(["✍️ Write Script", "📄 Upload PDF"])
script_content = ""
pdf_file=None

with tab1:
    user_script = st.text_area(
        label = "Script Input",
        placeholder="write the script here...",
        label_visibility="collapsed"
        )
    if user_script:
        script_content=user_script
with tab2:
    pdf_file = st.file_uploader("Upload Script PDF", type =["pdf"])

st.divider()


# 2. Bottom Section: Split View
if uploaded_video:
    col1, col2 = st.columns([2, 1]) # Col 1 is twice as wide as Col 2

    with col1:
        st.video(uploaded_video)
        if pdf_file:
            st.success("✅ PDF Script Uploaded and Processed!")
        elif script_content:
            st.success("✅ Manual Script Provided!")

    with col2:
        st.subheader("Analysis")
        st.write("Ready to check your video against the script.")
        
        # The Analyze Button
        if st.button("🚀 Run Analysis", use_container_width=True):
            if not script_content:
                st.error("Please provide a script first!")
            else:
                st.info("Sending to Gemini API...")
                # Your Gemini API Call Logic here