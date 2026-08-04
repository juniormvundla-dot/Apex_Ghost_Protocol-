import time
import math
import ctypes
import threading
from datetime import datetime
from ctypes import wintypes

# Win32 structure and function mappings using ctypes
user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Global state variables for tracking telemetry
cognitive_state = "neutral"
telemetry_lock = threading.Lock()

class CognitiveMonitor:
    """
    Background daemon measuring typing delays and mouse coordinates 
    using native Windows user32 APIs to deduce developer flow state.
    """
    def __init__(self, sample_interval_ms=100, window_duration_sec=60):
        self.sample_interval = sample_interval_ms / 1000.0
        self.window_duration = window_duration_sec
        self.running = False
        self.thread = None
        
        # In-memory telemetry log arrays
        self.key_timestamps = []
        self.mouse_movements = []  # List of velocities
        self.last_pos = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("[Cognitive Monitor] Background telemetry daemon started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _get_mouse_pos(self):
        pt = POINT()
        if user32.GetCursorPos(ctypes.byref(pt)):
            return pt.x, pt.y
        return None

    def _check_keys(self):
        # Poll standard virtual keys (A-Z: 0x41 to 0x5A, Space: 0x20, Back: 0x08, Enter: 0x0D, Tab: 0x09)
        # GetAsyncKeyState returns short with most significant bit set if key is currently pressed
        pressed = False
        for vk in range(8, 256):
            # Skip checking mouse keys (1, 2, 4)
            if vk in (1, 2, 4):
                continue
            if user32.GetAsyncKeyState(vk) & 0x8000:
                pressed = True
                break
        return pressed

    def _monitor_loop(self):
        last_key_state = False
        
        while self.running:
            now = time.time()
            
            # 1. Capture keyboard inputs
            key_pressed = self._check_keys()
            if key_pressed and not last_key_state:
                # Key down edge triggered
                self.key_timestamps.append(now)
            last_key_state = key_pressed
            
            # 2. Capture mouse movements
            pos = self._get_mouse_pos()
            if pos:
                if self.last_pos and self.last_pos != pos:
                    # Calculate Euclidean distance as velocity proxy
                    dx = pos[0] - self.last_pos[0]
                    dy = pos[1] - self.last_pos[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    self.mouse_movements.append((now, dist))
                self.last_pos = pos
                
            # 3. Trim telemetry logs outside window
            cutoff = now - self.window_duration
            self.key_timestamps = [t for t in self.key_timestamps if t > cutoff]
            self.mouse_movements = [m for m in self.mouse_movements if m[0] > cutoff]
            
            # 4. Analyze state every 60s
            if int(now) % 60 == 0:
                self._analyze_cognitive_state()
                
            time.sleep(self.sample_interval)

    def _analyze_cognitive_state(self):
        global cognitive_state
        
        # Calculate typing metrics
        keystroke_count = len(self.key_timestamps)
        delays = []
        if keystroke_count > 1:
            for i in range(1, keystroke_count):
                delays.append(self.key_timestamps[i] - self.key_timestamps[i-1])
                
        # Calculate standard deviation of keystroke delays
        delay_variance = 0.0
        if len(delays) > 1:
            mean = sum(delays) / len(delays)
            variance = sum((d - mean) ** 2 for d in delays) / len(delays)
            delay_variance = math.sqrt(variance)

        # Calculate mouse movement speed variance
        mouse_count = len(self.mouse_movements)
        mouse_variance = 0.0
        if mouse_count > 1:
            speeds = [m[1] for m in self.mouse_movements]
            mean_speed = sum(speeds) / len(speeds)
            var_speed = sum((s - mean_speed) ** 2 for s in speeds) / len(speeds)
            mouse_variance = math.sqrt(var_speed)

        # Classify state
        new_state = "neutral"
        with telemetry_lock:
            if keystroke_count > 25 and delay_variance < 0.25:
                # Fast, consistent typing cadence -> flow state
                new_state = "flow"
            elif keystroke_count > 5 and (delay_variance > 1.2 or mouse_variance > 80.0):
                # slow, erratic keystrokes or hyper-chaotic mouse entropy -> fatigue
                new_state = "fatigue"
                
            if new_state != cognitive_state:
                cognitive_state = new_state
                self._trigger_state_action(cognitive_state)

    def _trigger_state_action(self, state):
        print(f"[Cognitive State Shift] Calculated developer state: {state.upper()}")
        
        # Try importing soundscape and voice triggers
        try:
            from automation.soundscape_engine import soundscape_engine
            from voice.tts import speak_text
            
            if state == "flow":
                # Speak dynamic congrats and lock soundscape to binaural beats
                # We play audio in a background thread to prevent blocking
                threading.Thread(
                    target=lambda: speak_text("Flow state detected. Sir, locking focus soundscapes."),
                    daemon=True
                ).start()
                soundscape_engine.play_profile("focus_beats")
                
            elif state == "fatigue":
                # Suggest break and trigger soft playlist crossfade
                threading.Thread(
                    target=lambda: speak_text("Hunter, I detect cognitive fatigue. Standard operations recommend a ten minute pause."),
                    daemon=True
                ).start()
                soundscape_engine.play_profile("rain")
                
        except Exception as e:
            print(f"[Cognitive Monitor] Action trigger error: {e}")

# Global monitor instance
cognitive_monitor = CognitiveMonitor()
