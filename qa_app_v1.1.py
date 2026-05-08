import streamlit as st
import ollama
import json
import pandas as pd
from datetime import datetime

#title and line

st.title("🎨 Render QA Auto-Tagger")
st.write("Upload a 3D render to automatically tag and critique it.")

#uploaded_file variable where uploaded file will be stored

uploaded_file = st.file_uploader("Upload a Render", type=["png", "jpg", "jpeg"])

#here is the prompt
prompt ="""Analyze this 3D render and respond in JSON format only.

Use exactly these three keys:
-"Keywords": a list of 5 descriptive tags
-"Lighting_type": a short description of the lighting
-"critique": one sentence on how to improve the composition"""
col1, col2 =st.columns(2)

#check if file is uploaded then read the file and show the uploaded file with caption
def file_analyzer():
    if uploaded_file is not None:
        image_bytes=uploaded_file.read()
        with col1:
            st.image(image_bytes, caption="Uploaded Render", use_container_width=True)
                       
        with col2:
            if st.button("🔍 Analyze"):
                response = ollama.chat(
                    model='llava',
                    messages=[{
                        'role': 'user',
                        'content': prompt,
                        'images': [image_bytes]
                    }],
                    format='json'
                )
                raw_json = response['message']['content']
                
                st.session_state['parsed_data'] = json.loads(raw_json)               
                parsed_data = st.session_state['parsed_data']
                
                row = {
                    "filename": uploaded_file.name,
                    "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "keywords": str(parsed_data["Keywords"]),
                    "lighting_type": parsed_data["Lighting_type"],
                    "critique": parsed_data["critique"]
                }
                                
                st.session_state['df'] = pd.DataFrame([row])

            if 'parsed_data' in st.session_state:
                st.write(st.session_state['parsed_data'])
                # with open("asset_library.csv", "rb") as f:
                st.info("📁 After downloading, upload a new render to continue.")
                csv_data = st.session_state['df'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Analysis CSV",
                    data=csv_data,
                    file_name="asset_analysis.csv",
                    mime="text/csv"

                )                      
                                
    else:
        st.warning("Upload an image file!")

try:
    file_analyzer()
except Exception as e:
    st.write(f"Something went wrong: {e}")

