import os
import json
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent

from storage.db import database_manager

CIRCADIAN_FILE = project_root / "storage" / "circadian_profile.json"

class CircadianOptimizer:
    """
    Analyses focus session history over 14 days to map personalized productivity peak
    and low-energy slots, allocating high-stakes quests accordingly.
    """
    def __init__(self):
        # Default fallback chronotype profile
        self.profile = {
            "peak_start": "06:30",
            "peak_end": "09:00",
            "slump_start": "14:00",
            "slump_end": "17:00",
            "last_calculated": None
        }
        self.load_profile()

    def load_profile(self):
        if CIRCADIAN_FILE.exists():
            try:
                self.profile = json.loads(CIRCADIAN_FILE.read_text(encoding="utf-8"))
            except:
                pass

    def save_profile(self):
        CIRCADIAN_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.profile["last_calculated"] = datetime.now().isoformat()
        CIRCADIAN_FILE.write_text(json.dumps(self.profile, indent=2), encoding="utf-8")

    def calculate_profile(self):
        """
        Query focus sessions to find hourly focus density.
        """
        try:
            # Query last 14 days of focus session starts
            rows = database_manager.fetch_all(
                "SELECT start_time FROM focus_sessions WHERE completed = 1"
            )
            if not rows:
                return

            hourly_counts = [0] * 24
            for row in rows:
                start_str = row["start_time"]
                try:
                    dt = datetime.fromisoformat(start_str)
                    hourly_counts[dt.hour] += 1
                except:
                    pass

            # Find peak 2-hour window (sliding sum)
            max_sum = -1
            peak_hour = 6 # fallback 06:00
            for h in range(24):
                h1 = h
                h2 = (h + 1) % 24
                h_sum = hourly_counts[h1] + hourly_counts[h2]
                if h_sum > max_sum:
                    max_sum = h_sum
                    peak_hour = h

            # Set peak window
            self.profile["peak_start"] = f"{peak_hour:02d}:00"
            self.profile["peak_end"] = f"{(peak_hour + 2) % 24:02d}:00"
            
            # Low productivity slump is usually 6-8 hours after peak start
            slump_hour = (peak_hour + 7) % 24
            self.profile["slump_start"] = f"{slump_hour:02d}:00"
            self.profile["slump_end"] = f"{(slump_hour + 3) % 24:02d}:00"

            self.save_profile()
            print(f"[Circadian Optimizer] Calculated peak window: {self.profile['peak_start']} - {self.profile['peak_end']}")
        except Exception as e:
            print(f"[Circadian Optimizer] Calculation error: {e}")

    def get_time_recommendation(self, difficulty: int, category: str, context_hint: str | None = None) -> str:
        """
        Suggest optimal context-aware hour window dynamically querying the local machine learning predictor.
        """
        try:
            from quests.predictive_engine import predictive_engine
            
            # Query peak and slump windows from the predictive engine
            windows = predictive_engine.get_circadian_peak_and_slump()
            peak_window = f"{windows['peak_start']} - {windows['peak_end']}"
            slump_window = f"{windows['slump_start']} - {windows['slump_end']}"

            hint = (context_hint or "").upper()
            cat = str(category).upper()

            # 1. Morning Routine / Awakening Anchor
            if hint == "WAKEUP" or "WAKE" in hint:
                return "05:00 - 07:30 (Morning Anchor)"

            # 2. Deep Work / High-Stakes Boss Trial
            if hint == "DEEP_WORK" or cat == "BOSS" or difficulty >= 4:
                return f"{peak_window} (AI Predicted Peak)"

            # 3. Light Recovery / Reading / Health Wind-Down
            if hint == "RECOVERY" or hint == "READING" or cat == "SIDE":
                return f"{slump_window} (AI Predicted Slump)"

            # 4. Evening Reflection
            if hint == "EVENING":
                return "19:00 - 21:30 (Evening Wind-Down)"

            # 5. Core Maintenance / Habit Flow
            if difficulty >= 3:
                return f"{peak_window} (AI Predicted Peak)"
            else:
                return "11:00 - 14:00 (Midday Focus)"
                
        except Exception as e:
            print(f"[Circadian Optimizer] Fallback to hardcoded recommendations due to: {e}")
            hint = (context_hint or "").upper()
            if hint == "WAKEUP":
                return "05:00 - 07:30 (Morning Anchor)"
            if difficulty >= 3 or str(category).upper() == "BOSS":
                return f"{self.profile['peak_start']} - {self.profile['peak_end']} (Peak Flow)"
            else:
                return "11:00 - 14:00 (Midday Focus)"

# Global optimizer instance
circadian_optimizer = CircadianOptimizer()
