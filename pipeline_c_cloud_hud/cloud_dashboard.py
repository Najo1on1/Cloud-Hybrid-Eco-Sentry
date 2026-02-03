import streamlit as st
import cv2
import time
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from neo4j import GraphDatabase
import PIL.Image

# --- CONFIGURATION ---
# Load API Key from the proxy folder's .env (going back 2 levels)
load_dotenv(dotenv_path="../pipeline_a_vision_proxy/.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Neo4j Config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "cloudpassword123")

# Rate Limit Settings (Safe for Free Tier)
COOLDOWN_SECONDS = 15 

# --- SETUP CLIENTS ---
if 'genai_client' not in st.session_state:
    st.session_state.genai_client = genai.Client(api_key=GOOGLE_API_KEY)

if 'neo4j_driver' not in st.session_state:
    st.session_state.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

# --- LOGIC FUNCTIONS ---
def get_protocols(hazards_list):
    """Robust, Case-Insensitive Brain Query."""
    actions = []
    full_text = " ".join(hazards_list)
    
    query = """
    MATCH (h:Hazard)-[:TRIGGERS]->(p:Protocol)
    WHERE toLower($hazard_text) CONTAINS toLower(h.keyword)
    RETURN p.action AS action, p.code AS code
    """
    try:
        with st.session_state.neo4j_driver.session() as session:
            result = session.run(query, hazard_text=full_text)
            for record in result:
                actions.append(f"{record['action']} ({record['code']})")
    except Exception as e:
        return [f"DB ERROR: {e}"]
        
    return list(set(actions)) if actions else ["MONITORING (No Action)"]

def analyze_frame(frame_path):
    """Sends frame to Google Gemini."""
    try:
        img = PIL.Image.open(frame_path)
        prompt = "Analyze this industrial scene for safety hazards. Return ONLY valid JSON with fields: status (SAFE/DANGER), hazards (list), description."
        
        response = st.session_state.genai_client.models.generate_content(
            model="gemini-flash-latest",
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return {"status": "ERROR", "hazards": [], "description": str(e)}

# --- UI LAYOUT ---
st.set_page_config(page_title="Cloud Sentinel HUD", layout="wide", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .big-font { font-size: 24px !important; font-weight: bold; }
    .danger-box { padding: 15px; border-radius: 10px; background-color: rgba(255, 75, 75, 0.2); border: 1px solid #FF4B4B; }
    .safe-box { padding: 15px; border-radius: 10px; background-color: rgba(0, 204, 153, 0.2); border: 1px solid #00CC99; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Cloud Sentinel: Satellite Command")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Drone Feed")
    video_placeholder = st.empty()

with col2:
    st.subheader("Intelligence Report")
    status_area = st.empty()
    st.divider()
    st.markdown("**Active Protocols:**")
    protocol_area = st.empty()
    st.divider()
    st.markdown("**Satellite Uplink Status:**")
    progress_bar = st.progress(0)
    log_area = st.empty()

# --- MAIN LOOP ---
start_btn = st.sidebar.button("🚀 CONNECT SATELLITE", type="primary")

if start_btn:
    cap = cv2.VideoCapture("../assets/hazard_feed.mp4")
    
    # Initialize so it triggers immediately on first run
    # We subtract COOLDOWN so the math thinks 15s have already passed
    last_analysis_time = time.time() - COOLDOWN_SECONDS
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.warning("Signal Lost: End of Feed.")
            break
        
        # 1. Display Video (Convert BGR to RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, use_container_width=True)
        
        # 2. Check Timer for AI Analysis
        current_time = time.time()
        time_since_last = current_time - last_analysis_time
        
        # --- MATH CLAMP (Prevents Crash) ---
        # Ensures value is ALWAYS between 0.0 and 1.0
        raw_progress = time_since_last / COOLDOWN_SECONDS
        safe_progress = max(0.0, min(1.0, raw_progress))
        progress_bar.progress(safe_progress)
        
        if time_since_last >= COOLDOWN_SECONDS:
            log_area.caption("📤 Uploading Snapshot...")
            
            # Save & Analyze
            cv2.imwrite("temp_hud_frame.jpg", frame)
            analysis = analyze_frame("temp_hud_frame.jpg")
            
            # Logic
            hazards = analysis.get('hazards', [])
            protocols = get_protocols(hazards)
            
            # Update UI
            if analysis.get('status') == 'DANGER':
                status_area.markdown(f"<div class='danger-box'>🚨 <b>DANGER DETECTED</b><br>{', '.join(hazards)}</div>", unsafe_allow_html=True)
                
                protocol_html = ""
                for p in protocols:
                    protocol_html += f"❌ {p}<br>"
                protocol_area.markdown(protocol_html, unsafe_allow_html=True)
            else:
                status_area.markdown("<div class='safe-box'>✅ <b>ALL SYSTEMS NORMAL</b></div>", unsafe_allow_html=True)
                protocol_area.markdown("<i>No active threats.</i>", unsafe_allow_html=True)
            
            last_analysis_time = time.time()
            log_area.caption(f"✅ Data Received. Cooldown active ({COOLDOWN_SECONDS}s).")

        # --- SLOWER LOOP (Prevents Media Error) ---
        # 0.05s = ~20 FPS (Plenty for a dashboard, easier on the browser)
        time.sleep(0.05)

    cap.release()