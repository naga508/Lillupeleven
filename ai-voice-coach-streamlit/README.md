
# AI Voice Coach – Streamlit Demo

Streamlit app that acts as your presentation + live demo UI for the ElevenLabs AI Voice Coach.

## Modes
- **Backend mode (recommended)**: calls your FastAPI backend on Cloud Run.
- **Direct mode**: calls OpenAI + ElevenLabs directly from Streamlit (for quick demos).

## Files
- `streamlit_app.py`
- `requirements.txt`

## Streamlit Cloud Secrets
**Backend mode:**
```toml
BACKEND_URL = "https://your-cloud-run-url"
USE_DIRECT = "false"
```

**Direct mode:**
```toml
USE_DIRECT = "true"
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
ELEVENLABS_API_KEY = "eleven-..."
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
```

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
