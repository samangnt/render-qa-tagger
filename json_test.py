import ollama
import json

# 1. The Prompt (You MUST explicitly mention JSON here)
prompt = "Describe a 3D asset of a wooden barrel. Output entirely in JSON format with exactly two keys: 'asset_type' and 'material'."

# 2. The API Call (Notice the format='json' argument)
response = ollama.chat(
    model='llama3.1:8b',
    messages=[{'role': 'user', 'content': prompt}],
    format='json'  # <--- THIS IS THE MAGIC KEY
)

# 3. The AI returns a string that looks like JSON. We need to convert it to a real Python dictionary.
raw_text = response['message']['content']
print("--- RAW AI OUTPUT ---")
print(raw_text)

# 4. Parse it!
parsed_data = json.loads(raw_text)

print("\n--- PYTHON DICTIONARY OUTPUT ---")
print("Asset:", parsed_data['asset_type'])
print("Material:", parsed_data['material'])