import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()  # this reads your .env file

import os
API_KEY = os.getenv("SARVAM_API_KEY")
print("Loaded key:", API_KEY[:8] + "..." if API_KEY else "Not found")

# Load your API key from environment variable
API_KEY = os.getenv("SARVAM_API_KEY")  # <-- name of the variable, not the key itself

if not API_KEY:
    print("❌ SARVAM_API_KEY is not set in your environment.")
    print("   Set it first, e.g.:")
    print("   Windows PowerShell: $env:SARVAM_API_KEY='your_key_here'")
    print("   Linux/Mac: export SARVAM_API_KEY='your_key_here'")
    exit(1)

# API endpoint and headers
url = "https://api.sarvam.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Simple test prompt
payload = {
    "model": "sarvam-m",
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! Can you briefly introduce yourself?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print("🔍 Sending test request to Sarvam API...")
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"HTTP Status: {resp.status_code}")
    data = resp.json()
    print("Raw API response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if "error" in data:
        print(f"❌ API Error: {data['error']}")
    else:
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if content:
            print("\n✅ API returned content:")
            print(content)
        else:
            print("\n⚠️ No content found in API response.")
except Exception as e:
    print(f"❌ Request failed: {e}")