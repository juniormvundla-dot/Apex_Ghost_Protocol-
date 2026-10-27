from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "my-video" / "public"
OUTPUT_MP3 = PUBLIC_DIR / "voiceover.mp3"
CONFIG_PATH = ROOT_DIR / "core" / "apex_ghost_config.json"

DEMO_SCRIPT = (
    "System Alert. Hunter awakening sequence initiated. "
    "Air-gapped core connected. Biometric astrolabe synchronized. "
    "Neural fatigue: zero percent. Focus Guard engaged. "
    "Daily contracts active. All cognitive telemetry and capital flows monitored in real time. "
    "You are no longer bound by ordinary limits. Welcome back, Hunter. "
    "The System has chosen you. Begin your ascent."
)


def load_config_key() -> tuple[str, str]:
    if not CONFIG_PATH.exists():
        return "", ""
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        private_mode = data.get("private_mode", {})
        api_key = private_mode.get("elevenlabs_api_key", "").strip()
        voice_id = private_mode.get("elevenlabs_voice_id", "nPczCjzI2devNBz1zQrb").strip()
        return api_key, voice_id
    except Exception as e:
        print(f"[WARN] Failed to read config: {e}")
        return "", ""


def generate_with_elevenlabs(api_key: str, voice_id: str) -> bool:
    import requests
    print(f"[SYSTEM] Connecting to ElevenLabs API (Voice ID: {voice_id})...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": DEMO_SCRIPT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.65,
            "similarity_boost": 0.75
        }
    }
    try:
        res = requests.post(url, json=data, headers=headers, timeout=30)
        if res.status_code == 200:
            OUTPUT_MP3.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_MP3.write_bytes(res.content)
            print(f"[SUCCESS] ElevenLabs audio saved to: {OUTPUT_MP3}")
            return True
        else:
            print(f"[ERROR] ElevenLabs responded with HTTP {res.status_code}: {res.text}")
            return False
    except Exception as exc:
        print(f"[ERROR] ElevenLabs request failed: {exc}")
        return False


def generate_with_edge_tts() -> bool:
    print("[SYSTEM] Generating high-fidelity neural voiceover via edge-tts (free fallback)...")
    import asyncio
    import edge_tts

    async def _run():
        communicate = edge_tts.Communicate(DEMO_SCRIPT, voice="en-GB-RyanNeural", rate="-4%", pitch="-2Hz")
        OUTPUT_MP3.parent.mkdir(parents=True, exist_ok=True)
        await communicate.save(str(OUTPUT_MP3))

    try:
        asyncio.run(_run())
        print(f"[SUCCESS] Neural audio saved to: {OUTPUT_MP3}")
        return True
    except Exception as exc:
        print(f"[ERROR] edge-tts generation failed: {exc}")
        return False


def main():
    api_key, voice_id = load_config_key()
    
    # Check if real API key exists
    if api_key and api_key != "YOUR_ELEVENLABS_API_KEY":
        success = generate_with_elevenlabs(api_key, voice_id)
        if success:
            sys.exit(0)
        print("[INFO] Falling back to neural TTS...")

    # If no ElevenLabs key configured, use free local neural edge-tts
    success = generate_with_edge_tts()
    if success:
        print("\n[NOTE] Audio generated using free neural voice (en-GB-RyanNeural).")
        print("To switch to your ElevenLabs account, paste your API key into core/apex_ghost_config.json")
    else:
        print("[FATAL] Could not generate audio file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
