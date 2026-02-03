import os
import time
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
import PIL.Image

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()

# 2. Initialize the New Client
client = genai.Client(api_key=api_key)

def analyze_image(image_path):
    """
    Sends an image to Google Gemini (New SDK) and asks for safety assessment.
    """
    print(f"☁️  Sending {image_path} to Cloud Sentinel...")
    start_time = time.time()

    try:
        # Load image using Pillow
        img = PIL.Image.open(image_path)

        # The Prompt
        prompt = "Analyze this industrial scene for safety hazards. Return ONLY valid JSON with fields: status (SAFE/DANGER), hazards (list), description."

        # 3. Call the API (New Syntax)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json" 
            )
        )

        # 4. Parse Response 
        result_text = response.text
        result = json.loads(result_text)

        latency = round(time.time() - start_time, 2)
        result['latency'] = latency
        return result

    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return {"status": "ERROR", "hazards": [], "description": str(e), "latency": 0}

# --- TEST BLOCK ---
if __name__ == "__main__":
    if os.path.exists("test_image.jpg"):
        report = analyze_image("test_image.jpg")
        print("\n--- 📡 SATELLITE RESPONSE ---")
        print(json.dumps(report, indent=2))
    else:
        print("Please download 'test_image.jpg' first.")