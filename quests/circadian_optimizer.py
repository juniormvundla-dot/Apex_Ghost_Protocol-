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

    def get_time_recommendation(self, difficulty, category):
        """
        Suggest correct hour window dynamically querying the local machine learning predictor.
        """
        try:
            from quests.predictive_engine import predictive_engine
            
            # Determine current weekday
            today_weekday = datetime.now().weekday()
            
            # Probe hourly probabilities from 6:00 to 22:00
            hourly_probs = []
            for h in range(6, 23):
                prob = predictive_engine.predict_focus_success_probability(h, today_weekday)
                hourly_probs.append((h, prob))
                
            # Find peak hour (highest probability) and slump hour (lowest probability)
            hourly_probs.sort(key=lambda x: x[1], reverse=True)
            
            peak_hour = hourly_probs[0][0]
            slump_hour = hourly_probs[-1][0]
            
            # Format recommended windows
            peak_window = f"{peak_hour:02d}:00 - {(peak_hour+2)%24:02d}:00"
            slump_window = f"{slump_hour:02d}:00 - {(slump_hour+3)%24:02d}:00"
            
            if difficulty >= 3 or category == "BOSS":
                return f"{peak_window} (AI Predicted Peak)"
            else:
                return f"{slump_window} (AI Predicted Slump)"
        except Exception as e:
            print(f"[Circadian Optimizer] Fallback to hardcoded recommendations due to: {e}")
            # Hard coding / high-priority quests -> peak window
            if difficulty >= 3 or category == "BOSS":
                return f"{self.profile['peak_start']} - {self.profile['peak_end']} (Peak Flow)"
            else:
                return f"{self.profile['slump_start']} - {self.profile['slump_end']} (Light Slot)"

# Global optimizer instance
circadian_optimizer = CircadianOptimizer()
