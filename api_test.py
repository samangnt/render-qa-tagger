import requests
import json

# 1. The destination (Paste your unique webhook.site URL here)
url = "https://webhook.site/2e6fbc07-1a21-4d4c-8343-e363253d5e3d"

# 2. The data you want to send (Notice it's just a Python dictionary!)
payload = {
    "project": "Cyberpunk Cityscape",
    "status": "Render Complete",
    "ai_tags": ["sci-fi", "neon", "night"],
    "message": "Hey Art Director, the new render is ready for review!"
}

# 3. We have to tell the server we are sending JSON data
headers = {
    "Content-Type": "application/json"
}

# 4. The Action: Send the POST request
print("Sending message to the server...")
response = requests.post(url, json=payload, headers=headers)

# 5. Check if it worked (Status Code 200 means "OK")
if response.status_code == 200:
    print("Success! Data sent.")
else:
    print(f"Failed. Server said: {response.status_code}")