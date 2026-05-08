import os
import requests
import streamlit as st
import ollama
import json
import pandas as pd
#from PIL import Image

#title and line

st.title("🎨 Render QA Auto-Tagger")
st.write("Upload a 3D render to automatically tag and critique it.")

#uploaded_file variable where uploaded file will be stored

uploaded_file = st.file_uploader("Upload a Render", type=["png", "jpg", "jpeg"])

#here is the prompt
prompt ="""Analyze this 3D render and respond in JSON format only.

Use exactly these three keys:
-"keywords": a list of 5 descriptive tags
-"lighting_type": a short description of the lighting
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
                parsed_data = {k.lower(): v for k, v in parsed_data.items()}
                
                # Notify Art Director automatically
                webhook_url = "https://webhook.site/2e6fbc07-1a21-4d4c-8343-e363253d5e3d"
                notification = {
                    "filename": uploaded_file.name,
                    "keywords": parsed_data["keywords"],
                    "lighting": parsed_data["lighting_type"],
                    "critique": parsed_data["critique"],
                    "message": "New render analyzed and ready for review!"
                }
                requests.post(webhook_url, json=notification)
                
                st.toast("📨 Art Director notified!")

                # Save to server silently
                
                row = {
                    "filename": uploaded_file.name,
                    "keywords": str(parsed_data["keywords"]),
                    "lighting_type": parsed_data["lighting_type"],
                    "critique": parsed_data["critique"]
                }
                df = pd.DataFrame([row])
                df.to_csv("asset_library.csv", mode='a',
                        header=not os.path.exists("asset_library.csv"),
                        index=False)

                if 'parsed_data' in st.session_state:
                    st.write(st.session_state['parsed_data'])
                    with open("asset_library.csv", "rb") as f:
                        st.download_button(
                            label="📥 Download Library CSV",
                            data=f,
                            file_name="asset_library.csv",
                            mime="text/csv"
                        )
                                
                        st.success("✅ Saved to asset_library.csv!")
                else:
                    st.warning("Upload an image file!")

try:
    file_analyzer()
except Exception as e:
    st.write(f"Something went wrong: {e}")

