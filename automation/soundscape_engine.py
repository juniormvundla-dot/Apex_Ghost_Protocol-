import subprocess
import os
import threading
from pathlib import Path

from core.config import config
from automation.awakening import MorningAwakeningProtocol

class SoundscapeEngine:
    """
    Coordinates headless VLC process execution to overlay context-aware audio
    frequencies matching active quest categories and developer fatigue states.
    """
    def __init__(self):
        self.active_process = None
        self.lock = threading.Lock()
        
        # Discover VLC path dynamically
        ap = MorningAwakeningProtocol()
        self.vlc_exe = ap._find_vlc_path() or Path(config.awakening.vlc_path)
        
        # Audio stream registry (Public Icecast/Zeno streaming relays)
        self.profiles = {
            "focus_beats": "http://178.32.107.135:8162/stream",       # Binaural / Meditation
            "lofi": "http://stream.zeno.fm/08w243a049duv",            # Lofi Chill
            "physical": "https://stream.radiorecord.ru/club_128.mp3", # High BPM Dance/Club
            "rain": "http://stream.zeno.fm/unv8262u45duv"             # Rain / Ambient noise
        }

    def play_profile(self, name):
        """
        Kill active player and launch new headless VLC stream.
        """
        if not self.vlc_exe.exists():
            print(f"[Soundscape Engine] Aborted. VLC executable not found at: {self.vlc_exe}")
            return

        stream_url = self.profiles.get(name)
        if not stream_url:
            print(f"[Soundscape Engine] Unknown soundscape profile: {name}")
            return

        with self.lock:
            # 1. Stop active process
            self.stop()
            
            # 2. Launch headless VLC daemon
            print(f"[Soundscape Engine] Spawning soundscape: {name} ({stream_url})")
            cmd = [
                str(self.vlc_exe),
                "--intf", "dummy",
                "--dummy-quiet",
                "--no-video",
                "--loop",
                stream_url
            ]
            
            try:
                # Startupinfo flags to prevent command window popup on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                self.active_process = subprocess.Popen(
                    cmd, 
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                print(f"[Soundscape Engine] Failed to play stream: {e}")

    def stop(self):
        """
        Force kill the running VLC stream process.
        """
        if self.active_process:
            try:
                self.active_process.terminate()
                self.active_process.wait(timeout=2)
            except:
                try:
                    self.active_process.kill()
                except:
                    pass
            self.active_process = None
            print("[Soundscape Engine] Audio stream terminated.")

# Global soundscape instance
soundscape_engine = SoundscapeEngine()
