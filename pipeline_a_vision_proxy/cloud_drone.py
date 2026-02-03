import cv2
import time
import json
import os
from neo4j import GraphDatabase
from vision_client import analyze_image

# --- CONFIG ---
VIDEO_PATH = "../assets/hazard_feed.mp4"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "cloudpassword123")

# --- LOGIC FUNCTION ---
def consult_brain(hazards_list):
    """Checks Neo4j for protocols (Case-Insensitive & Robust)."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    actions = []

    # 1. Join the list into a single string
    full_text = " ".join(hazards_list)

    # 2. Convert BOTH sides to lowercase in the query
    query = """
    MATCH (h:Hazard)-[:TRIGGERS]->(p:Protocol)
    WHERE toLower($hazard_text) CONTAINS toLower(h.keyword)
    RETURN p.action AS action, p.code AS code
    """

    try:
        with driver.session() as session:
            result = session.run(query, hazard_text=full_text)
            for record in result:
                actions.append(f"{record['action']} ({record['code']})")
    except Exception as e:
        return [f"DB_ERROR: {e}"]
    finally:
        driver.close()

    return list(set(actions)) if actions else ["LOG_OBSERVATION (No Protocol)"]

# --- MAIN LOOP ---
print(f"🚀 CLOUD SENTINEL: SYSTEM ONLINE")
print(f"📂 Feed: {VIDEO_PATH}")

cap = cv2.VideoCapture(VIDEO_PATH)
frame_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Check every 10 seconds (Rate Limit Safe)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = int(fps * 20) 

        if frame_count % interval == 0:
            print(f"\n[Frame {frame_count}] 📸 Analyzing...")
            cv2.imwrite("temp_cloud_frame.jpg", frame)

            # 1. VISION (Gemini)
            analysis = analyze_image("temp_cloud_frame.jpg")
            hazards = analysis.get('hazards', [])
            latency = analysis.get('latency', 0)

            # 2. LOGIC (Neo4j)
            protocols = consult_brain(hazards)

            # 3. REPORT
            print(f"   ☁️  Gemini ({latency}s): Found {len(hazards)} hazards")
            if hazards:
                print(f"   ⚠️  DETECTED: {hazards}")
                print(f"   🧠  PROTOCOL: {protocols}")
            else:
                print("   🟢  STATUS: Safe")

            # Rate Limit Sleep
            print("   ⏳ Cooling down (15s)...")
            time.sleep(15)

        frame_count += 1

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
cap.release()