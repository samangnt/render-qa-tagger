import os
import io
from google import generativeai as genai
import pandas as pd
import streamlit as st
import json
import datetime
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

SYSTEM_PROMPT = """
You are an elite Technical Animation and Lighting Supervisor. Your job is to perform a strict "Script-to-Screen" audit by comparing a provided 3D render sequence (video) against the approved scene script (provided as text or pdf).

CRITICAL DIRECTIVE: You must output TEXT ONLY in the requested JSON format. DO NOT generate, output, or attempt to create any video, audio, or image files.

Your primary directive is accuracy. DO NOT hallucinate errors. If you are not 100 percent certain about a technical clipping issue, action mismatch, or lighting artifact due to video resolution or framing, DO NOT flag it. You operate on a "Guilty Beyond a Reasonable Doubt" framework.

Evaluate the render against the script based on these four criteria:
1. Action Verification: Do the physical actions in the render match the explicit script directions?
2. Timing & Pacing: Does the timing of the actions feel natural and align with the intended flow of the scene?
3. Lighting & Composition: Does the lighting setup, shadow placement, and camera framing match the requested mood? Detect any sudden lighting pops, missing shadows, or flickers.
4. Emotional Alignment: Does the character posture and overall atmosphere reflect the intended emotion of the script?

You must output your audit STRICTLY in valid JSON format. Do not include any conversational text before or after the JSON. 

Use the following JSON schema:
{
  "readiness_grade": "[Assign a grade: A, B, C, D, or F based on adherence to the script]",
  "summary": "[One short paragraph summarizing the overall execution]",
  "timestamped_feedback": [
    {
      "timestamp": "[Format: MM:SS]",
      "category": "[Choose one: Action Mismatch, Timing/Pacing, Lighting & Composition, Emotional Alignment, or Technical Flaw]",
      "critique": "[Provide specific, constructive feedback on what is wrong and how to fix it]"
    }
  ]
}
"""

# Development mode — uses only one model
DEV_MODE = True
#this selects the ai model then reads media_part that is video

def get_ai_response(system_prompt, script_payload, media_part):
    
    # We bundle everything into one list for Gemini to read
    request_content = [
        system_prompt, 
        "HERE IS THE APPROVED SCRIPT:", 
        script_payload, 
        "HERE IS THE RENDER TO ANALYZE:", 
        media_part
    ]
    
    # Development — single model only
    if DEV_MODE:
        model = genai.GenerativeModel(MODELS[2]) 
        return model.generate_content(request_content)
    
    # Production — fallback chain
    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(request_content)
            st.caption(f"⚡ Powered by {model_name}")
            return response
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue  
            else:
                raise e  
    
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

# The Injection
final_script_payload = None

if uploaded_video:
    col1, col2 = st.columns([2, 1]) # Col 1 is twice as wide as Col 2

    with col1:
        st.video(uploaded_video)
        # We check the PDF FIRST, because you want to prefer it
        if pdf_file is not None:
            # Package the raw PDF bytes for Gemini
            final_script_payload = {
                "mime_type": "application/pdf",
                "data": pdf_file.getvalue()
            }
            st.success("PDF Script loaded!")

        # If no PDF, check if they typed something in the text area
        elif user_script and user_script.strip() != "":
            final_script_payload = user_script
            st.success("Text Script loaded!")

    with col2:
        st.subheader("Analysis")
        st.write("Ready to check your video against the script.")
        
        # The Analyze Button
        if st.button("🚀 Run Analysis", use_container_width=True):
            if not script_content and not pdf_file:
                st.error("Please provide a script first!")
            else:
                st.info("Sending to Gemini API...")
                # Your Gemini API Call Logic here
                get_ai_response(final_script_payload, user_script)