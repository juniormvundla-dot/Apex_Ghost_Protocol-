from __future__ import annotations

# This file provides a Windows-native text-to-speech helper.
# It uses the built-in SAPI voice engine through pywin32.
# This is often more reliable on Windows than pyttsx3.

import time
import requests
from pathlib import Path
from core.paths import paths
from core.config import config


def speak_via_elevenlabs(text: str) -> bool:
    """
    Attempt to speak the text using ElevenLabs API and play the generated audio.
    Returns True if successful, False if it failed/should fallback to SAPI.
    """
    api_key = getattr(config.private_mode, "elevenlabs_api_key", "")
    voice_id = getattr(config.private_mode, "elevenlabs_voice_id", "")
    
    if not api_key:
        print("ElevenLabs API Key is not set in config. Falling back to SAPI voice.")
        return False
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        print("Connecting to ElevenLabs API for Jarvis voice...")
        try:
            response = requests.post(url, json=data, headers=headers, timeout=20)
        except requests.exceptions.SSLError:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(url, json=data, headers=headers, timeout=20, verify=False)
            
        if response.status_code != 200:
            print(f"ElevenLabs API returned status code {response.status_code}: {response.text}")
            return False
            
        temp_audio_path = paths.assets_dir / "elevenlabs_temp.mp3"
        temp_audio_path.write_bytes(response.content)
        
        # Play using Windows MCI (Media Control Interface) via ctypes
        import ctypes
        safe_path = str(temp_audio_path).replace("\\", "/")
        ctypes.windll.winmm.mciSendStringW(f'open "{safe_path}" type mpegvideo alias mymp3', None, 0, None)
        ctypes.windll.winmm.mciSendStringW('play mymp3 wait', None, 0, None)
        ctypes.windll.winmm.mciSendStringW('close mymp3', None, 0, None)
            
        return True
    except Exception as exc:
        print(f"ElevenLabs TTS failed: {exc}")
        return False


def speak_text(text: str, voice_preference: str | None = None) -> None:
    """
    Speak the given text aloud. Attempts ElevenLabs first if enabled, falling back to SAPI.
    """
    if getattr(config.private_mode, "use_elevenlabs", False):
        success = speak_via_elevenlabs(text)
        if success:
            return

    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass

    try:
        import win32com.client

        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        if voice_preference:
            voices = speaker.GetVoices()
            selected_voice = None
            pref_lower = voice_preference.lower()
            for voice in voices:
                desc = voice.GetDescription().lower()
                if pref_lower in desc:
                    selected_voice = voice
                    break
            
            if selected_voice:
                speaker.Voice = selected_voice

        speaker.Speak(text)

    except Exception as exc:
        print(f"[TTS fallback] {text}")
        print(f"TTS error: {exc}")
    finally:
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass