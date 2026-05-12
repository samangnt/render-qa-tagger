import io
from google import generativeai as genai
import pandas as pd
import streamlit as st
import json
import datetime
import pypdf

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# All available models in priority order
MODELS = [
    'gemini-3.0-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite'
]


# Development mode — uses only one model
DEV_MODE = True
#this selects the ai model
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
uploaded_file = st.file_uploader(
    "Upload Video (Max 1080p, 30fps, 1min)", 
    type=["mp4", "mov", "avi", "webm", "wmv"]
)

#2. Script uploader with text area
tab1, tab2 = st.tabs(["✍️ Write Script", "📄 Upload PDF"])
script_content = ""
with tab1:
    user_script = st.text_area(
    label = "Script Input",
    placeholder="write the script here..."
    label_visibility="collapsed"
    )
with tab2:
    pdf_file = st.file_uploader("Upload Script PDF", type =["pdf"])
    if pdf_file:
        reader=pypdf.PdfReader(pdf_file)
        script_content="".join([page.extract_text() for page in reader.pages])

st.divider()


col1, col2 = st.columns(2)
if uploaded_file is not None:
    st.video(uploaded_file)
    st.success("video uploaded Successfully!")
    with col1:
        st.image(image_bytes, caption="Uploaded Video", use_container_width=True)
    with col2:
        st