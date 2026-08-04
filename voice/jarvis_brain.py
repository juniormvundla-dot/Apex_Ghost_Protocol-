import os
import requests
from core.config import config
from voice.script_builder import build_private_mode_script, build_intelligence_script

def generate_jarvis_briefing(
    hunter_name: str, 
    rank: str, 
    streak: int, 
    north_star: str, 
    pending_quests: int
) -> str | None:
    """
    Query the Gemini API to synthesize the player's stats into an immersive, professional, 
    motivating greeting spoken in J.A.R.V.I.S.'s signature British style.
    """
    api_key = getattr(config.private_mode, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[J.A.R.V.I.S.] Gemini API Key not found. Engaging zero-AI deterministic script builder...")
        return build_private_mode_script(hunter_name, rank, streak, north_star, pending_quests)
        
    model = getattr(config.private_mode, "gemini_model", "gemini-2.0-flash")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Route credentials based on key type (AQ. Pro keys require Bearer Token authorization)
    if api_key.startswith("AQ."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers["Authorization"] = f"Bearer {api_key}"
        headers["x-goog-api-key"] = api_key
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    prompt = (
        "You are J.A.R.V.I.S., the legendary AI assistant created by Tony Stark. "
        "You speak with a warm, formal, slightly dry British tone, addressing the user as 'Sir'. "
        "Your goal is to synthesize the following player stats into an immersive, motivating, "
        "and brief announcement for when focus/workspace protocols are activated: "
        f"- Player Name: Hunter {hunter_name}\n"
        f"- Current Rank: {rank}\n"
        f"- Login/Discipline Streak: {streak} days active\n"
        f"- North Star Goal: {north_star or 'Not set'}\n"
        f"- Daily Quests/Objectives Remaining: {pending_quests}\n\n"
        "Requirements:\n"
        "1. Strictly keep the response between 2 to 3 sentences long.\n"
        "2. Do not use any markdown (no asterisks, hash tags, or bold characters) as this will be read aloud by TTS.\n"
        "3. Focus on a clean, professional, immersive tone. Let's engage."
    )
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
        except requests.exceptions.SSLError:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
            
        if response.status_code != 200:
            print(f"Gemini API returned status code {response.status_code}: {response.text}")
            print("[J.A.R.V.I.S.] Falling back to zero-AI deterministic script builder...")
            return build_private_mode_script(hunter_name, rank, streak, north_star, pending_quests)
            
        result = response.json()
        candidates = result.get("candidates", [])
        if not candidates:
            return build_private_mode_script(hunter_name, rank, streak, north_star, pending_quests)
            
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return build_private_mode_script(hunter_name, rank, streak, north_star, pending_quests)
            
        text = parts[0].get("text", "")
        return text.strip().replace("\n", " ")
        
    except Exception as exc:
        print(f"Failed to query Gemini API: {exc}. Engaging zero-AI deterministic script builder...")
        return build_private_mode_script(hunter_name, rank, streak, north_star, pending_quests)

def generate_intelligence_script(trend_content: str, security_content: str) -> str | None:
    """
    Query the Gemini API to summarize raw intelligence data into a short, 
    conversational spoken script.
    """
    api_key = getattr(config.private_mode, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[J.A.R.V.I.S.] Gemini API Key not set. Engaging zero-AI deterministic intelligence script...")
        return build_intelligence_script(trend_content, security_content)
        
    model = getattr(config.private_mode, "gemini_model", "gemini-2.0-flash")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key.startswith("AQ."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers["Authorization"] = f"Bearer {api_key}"
        headers["x-goog-api-key"] = api_key
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    prompt = (
        "You are J.A.R.V.I.S., the legendary AI assistant created by Tony Stark. "
        "You speak with a warm, formal, slightly dry British tone, addressing the user as 'Sir'. "
        "Your goal is to synthesize the following intelligence brief into a concise, conversational update "
        "meant to be spoken aloud via TTS. "
        f"\n\n--- Tech Trends ---\n{trend_content}\n\n"
        f"--- Security Findings ---\n{security_content}\n\n"
        "Requirements:\n"
        "1. Start with a brief greeting like 'Sir, I have compiled your intelligence brief for today.'\n"
        "2. Summarize the most critical or interesting tech trends in 1-2 sentences.\n"
        "3. Mention any critical security findings, or state that the perimeter is secure if none.\n"
        "4. Keep the entire response under 4 sentences.\n"
        "5. Do not use any markdown (no asterisks, hash tags, or bold characters) as this will be read aloud by TTS.\n"
        "6. Do not include introductory text like 'Here is the script'. Just output the spoken text."
    )
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        try:
            response = requests.post(url, json=data, headers=headers, timeout=15)
        except requests.exceptions.SSLError:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(url, json=data, headers=headers, timeout=15, verify=False)
            
        if response.status_code != 200:
            print(f"Gemini API returned status code {response.status_code}: {response.text}")
            print("[J.A.R.V.I.S.] Falling back to deterministic intelligence script...")
            return build_intelligence_script(trend_content, security_content)
            
        result = response.json()
        candidates = result.get("candidates", [])
        if not candidates:
            return build_intelligence_script(trend_content, security_content)
            
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return build_intelligence_script(trend_content, security_content)
            
        text = parts[0].get("text", "")
        return text.strip().replace("\n", " ")
        
    except Exception as exc:
        print(f"Failed to query Gemini API for intelligence: {exc}. Engaging deterministic script...")
        return build_intelligence_script(trend_content, security_content)
