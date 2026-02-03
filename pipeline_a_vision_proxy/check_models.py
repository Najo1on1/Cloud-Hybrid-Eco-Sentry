import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Scanning available models...")
try:
    # Just print the name, don't check for specific methods
    for m in client.models.list():
        print(f"✅ FOUND: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")