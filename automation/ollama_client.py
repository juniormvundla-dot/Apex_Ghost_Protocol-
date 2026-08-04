import json
import urllib.request
import urllib.error

class OllamaClient:
    """
    Lightweight, dependency-free local client connection routing prompt requests
    to local Ollama model APIs (e.g. Llama-3 / Phi-3) on Port 11434.
    """
    def __init__(self, host="localhost", port=11434, model="llama3"):
        self.url = f"http://{host}:{port}/api/generate"
        self.model = model

    def check_connection(self):
        """
        Quick check if local Ollama daemon is active.
        """
        try:
            # Send brief request to check responsiveness
            req = urllib.request.Request(
                self.url.replace("/api/generate", "/"),
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=1.5) as response:
                return response.status == 200
        except Exception:
            return False

    def query(self, prompt, system_prompt=None):
        """
        Send generative completion request to local LLM, returning text response.
        """
        if not self.check_connection():
            print("[Ollama Client] Offline. Falling back to rule-based templates.")
            return None

        # Build request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            headers = {"Content-Type": "application/json"}
            data = json.dumps(payload).encode("utf-8")
            
            req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    return resp_data.get("response", "").strip()
        except urllib.error.URLError as ue:
            print(f"[Ollama Client] URLError: {ue}")
        except Exception as e:
            print(f"[Ollama Client] Request failed: {e}")
            
        return None

# Global reusable instance
ollama_client = OllamaClient()
