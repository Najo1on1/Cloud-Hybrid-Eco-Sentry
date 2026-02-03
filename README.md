# 👁️ Eco Sentry: Autonomous Industrial Overwatch

**Protecting infrastructure and personnel with intelligent, context-aware monitoring.**

Eco Sentry goes beyond simple motion detection. It is an intelligent agent capable of understanding complex industrial scenes identifying structural collapses, chemical spills, and fire hazards and instantly recommending the correct ISO/OSHA safety protocols.

Built on a **Hybrid Cloud** architecture, it combines the infinite context window of **Google Gemini** with the rigid reliability of a **Graph Database**, ensuring that safety officers get accurate, actionable intelligence without the noise.

---

## 🚀 How It Works

Eco Sentry operates as a "Satellite Command" unit. It watches the live drone feed and periodically uplinks a high-resolution snapshot for deep analysis.

### The Workflow

1. **See:** The **Vision Proxy** captures a high-definition frame from the drone feed.
2. **Analyze:** The image is sent to **Google Gemini**, which analyzes the scene for potential threats (e.g., "The roof of Building A has collapsed").
3. **Decide:** The system queries the **Logic Core (Neo4j)** to find the specific protocol for "Roof Collapse."
4. **Act:** The **Cloud HUD** alerts the operator with a `CRITICAL ALERT` and displays the `STRUCTURAL_LOCKDOWN` procedure.

---

## 🛡️ Safety by Design

In safety-critical systems, ambiguity is dangerous. Eco Sentry uses a **Deterministic Logic Graph** to ensure that AI variability never compromises safety.

The system acts as a filter: it takes the "fuzzy" natural language from the AI and forces it through a strict normalization layer. This guarantees that whether the AI says "Fire," "Blaze," or "Smoke," the system **always** triggers the `ACTIVATE_SPRINKLERS` protocol.

---

## ⚡ Performance & Reliability

Eco Sentry is designed for the real world, where bandwidth varies and API costs matter.

* **Live Video:** The operator always sees a smooth, real-time video feed.
* **Asynchronous Intelligence:** Heavy AI processing happens in the background.
* **Rate-Limit Protection:** A built-in "Cooldown" system ensures the platform stays within API quotas (Free Tier friendly) without crashing or freezing.

---

## 💻 Getting Started

### 1. Setup the Environment

```bash
git clone https://github.com/yourusername/eco-sentry.git
# Create .env with GOOGLE_API_KEY in pipeline_a_vision_proxy/

```

### 2. Initialize the Brain

```bash
cd cloud_hybrid_route/pipeline_b_cloud_logic
docker compose up -d
python3 init_cloud_rules.py

```

### 3. Start the Mission

```bash
cd ../pipeline_c_cloud_hud
streamlit run cloud_dashboard.py

```

## 📂 Project Structure

```text
cloud_hybrid_route/
├── assets/
│   └── hazard_feed.mp4        # Test footage
├── images/                    # Architecture diagrams
├── pipeline_a_vision_proxy/   # THE EYES
│   ├── vision_client.py       # Gemini API Client
│   ├── cloud_drone.py         # Headless processing script
│   └── .env                   # API Credentials
├── pipeline_b_cloud_logic/    # THE BRAIN
│   ├── docker-compose.yaml    # Neo4j Container config
│   └── init_cloud_rules.py    # Knowledge Graph Loader
└── pipeline_c_cloud_hud/      # THE FACE
    └── cloud_dashboard.py     # Streamlit Interface

```

## 📄 License

MIT License. See `LICENSE` for details.