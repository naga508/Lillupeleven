
import os, textwrap, httpx, streamlit as st

st.set_page_config(page_title="AI Voice Coach – Demo & Pitch", page_icon="🎧", layout="wide")

USE_DIRECT = st.secrets.get("USE_DIRECT", os.getenv("USE_DIRECT", "false")).lower() == "true"
BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8080"))

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
ELEVEN_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY", ""))
ELEVEN_VOICE_ID = st.secrets.get("ELEVENLABS_VOICE_ID", os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"))

def pitch_script():
    return textwrap.dedent('''
    ### 90-second elevator
    **Problem:** Busy people want better habits, but text-heavy apps are easy to ignore and lack real-time feedback.  
    **Solution:** A push-to-talk **AI Voice Coach** that replies in 60–120 seconds with practical, personalized guidance—spoken back via ElevenLabs.  
    **Target:** Professionals (20–45), students, creators.  
    **Why us:** Hands-free, fast, supportive tone; multilingual.  
    **Model:** Freemium → Pro ($7.99/mo or $59/yr).  
    **Metrics:** Weekly active sessions/user, trial→paid, 30-day retention.  
    **Risks:** Latency & privacy → streaming + short retention + delete.  
    **Roadmap:** MVP single-coach → V1 dual-coach + translation → V2 dashboards & marketplace.
    ''')

def openai_chat(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {"model": OPENAI_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
    with httpx.Client(timeout=60) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

def elevenlabs_tts(text: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "accept": "audio/mpeg", "content-type": "application/json"}
    payload = {"text": text, "model_id": "eleven_multilingual_v2",
               "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}}
    with httpx.Client(timeout=120) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.content

def build_prompt(user_text: str, mode: str) -> str:
    if mode == "dual":
        return ("You are 'Mentor'—authoritative, warm, practical.\n"
                "You are 'Learner'—curious, reflective, asks clarifying questions.\n"
                f"User: {user_text}\n"
                "Have Mentor speak first (2 short sentences) then Learner (2 short sentences).")
    return ("You are a supportive, concise voice coach. "
            "Keep answers short, practical, and motivating. "
            "If asked for plans, list at most 3 bullets.\n"
            f"User: {user_text}")

def call_backend_text(text: str, mode: str, voice_id: str | None):
    data = {"text": text, "mode": mode}
    if voice_id:
        data["voice_id"] = voice_id
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{BACKEND_URL}/v1/session/turn/text", data=data)
        r.raise_for_status()
        return r.json()

st.markdown("<h1 style='margin-bottom:0'>🎧 AI Voice Coach</h1>", unsafe_allow_html=True)
st.caption("Mind map + pitch + live demo (LLM → ElevenLabs)")

st.toggle("Direct mode (no backend)", value=USE_DIRECT, key="direct_toggle")
USE_DIRECT = st.session_state["direct_toggle"]

tabs = st.tabs(["🗺️ Mind Map", "🗣️ Live Demo", "🧾 Pitch Script", "⚙️ Setup"])

with tabs[0]:
    st.subheader("Architecture Mind Map")
    st.markdown("""
    **Core Modules:** STT (GCP/Whisper), LLM (Gemini/OpenAI/Claude), TTS (ElevenLabs), Translation (GCP), Billing (Stripe)  
    **Cloud:** API Gateway, Cloud Run, Firestore, GCS, Secret Manager  
    **Frontend:** React Native/Expo, Web dashboard (future)  
    **Data Flow:** Voice → STT → LLM → TTS → GCS → Playback
    """)

with tabs[1]:
    st.subheader("LLM → ElevenLabs Voice")
    mode = st.selectbox("Mode", ["single", "dual"], index=0)
    voice_id_opt = st.text_input("ElevenLabs Voice ID (optional; blank uses default)")
    text = st.text_area("Your prompt", "Give me a 60-second focus breathing routine.")
    if st.button("Generate & Speak", type="primary"):
        if USE_DIRECT:
            if not OPENAI_API_KEY or not ELEVEN_API_KEY:
                st.error("Missing OPENAI_API_KEY or ELEVENLABS_API_KEY. Add them in Streamlit Secrets.")
            else:
                with st.spinner("Thinking…"):
                    reply = openai_chat(build_prompt(text, mode))
                    mp3 = elevenlabs_tts(reply)
                st.success("Reply")
                st.write(reply)
                st.audio(mp3, format="audio/mp3")
        else:
            with st.spinner("Calling backend…"):
                out = call_backend_text(text, mode, voice_id_opt.strip() or None)
            st.success("Reply")
            st.write(out["reply"])
            st.audio(out["audio_url"])

with tabs[2]:
    st.subheader("Presentation Script")
    st.markdown(pitch_script())

with tabs[3]:
    st.subheader("How to Run")
    st.markdown("""
**Backend mode (recommended):**
1. Deploy your FastAPI backend to Cloud Run.
2. In Streamlit Cloud → **Secrets**, set:
```toml
BACKEND_URL = "https://your-cloud-run-url"
USE_DIRECT = "false"
```
3. Deploy this app and present from the **Live Demo** tab.

**Direct mode (single-file demo):**
1. In Streamlit Cloud → **Secrets**, set:
```toml
USE_DIRECT = "true"
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
ELEVENLABS_API_KEY = "eleven-..."
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
```
2. Run and present without a backend (demo-friendly; keep keys in Secrets).

*Never hardcode API keys in code or commit history.*
""")
