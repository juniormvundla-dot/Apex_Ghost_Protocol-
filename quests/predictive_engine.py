import os
import json
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent

from storage.db import database_manager

class PredictiveEngine:
    """
    Local Machine Learning prediction engine using Scikit-Learn Random Forests
    to forecast developer focus session success probability at any given hour.
    """
    def __init__(self):
        self.model = None
        self.min_samples_to_train = 8

    def _load_data_and_train(self):
        """
        Extract tabular logs from SQLite focus history and fit a Random Forest model.
        """
        try:
            import pandas as pd
            import numpy as np
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            # ML libraries still installing or unavailable
            return False

        try:
            database_manager.ensure_ready()
            rows = database_manager.fetch_all("SELECT start_time, end_time, completed FROM focus_sessions")
            
            if len(rows) < self.min_samples_to_train:
                return False

            # Compile feature rows
            data_list = []
            for row in rows:
                try:
                    dt = datetime.fromisoformat(row["start_time"])
                    completed = int(row["completed"] == 1)
                    
                    data_list.append({
                        "hour": dt.hour,
                        "weekday": dt.weekday(),
                        "label": completed
                    })
                except:
                    continue

            if len(data_list) < self.min_samples_to_train:
                return False

            df = pd.DataFrame(data_list)
            X = df[["hour", "weekday"]]
            y = df["label"]

            # Train a Random Forest model
            self.model = RandomForestClassifier(n_estimators=30, max_depth=3, random_state=42)
            self.model.fit(X, y)
            return True
        except Exception as e:
            print(f"[Predictive Engine] Training exception: {e}")
            return False

    def predict_focus_success_probability(self, hour=None, weekday=None):
        """
        Predict probability (0.0 to 1.0) of successfully completing a deep-work block 
        at the specified hour and weekday.
        """
        if hour is None:
            hour = datetime.now().hour
        if weekday is None:
            weekday = datetime.now().weekday()

        # 1. Try to train local model dynamically
        trained = self._load_data_and_train()
        
        # 2. If model is available, return machine learning prediction
        if trained and self.model is not None:
            try:
                import pandas as pd
                # Predict probability distribution (classes: 0 = aborted, 1 = completed)
                input_df = pd.DataFrame([[hour, weekday]], columns=["hour", "weekday"])
                probs = self.model.predict_proba(input_df)[0]
                # Class 1 probability is target
                return float(probs[1])
            except Exception as e:
                print(f"[Predictive Engine] Prediction error: {e}")

        # 3. Fallback: Heuristic circadian peak matching (Chronobiology)
        # Deep Work Peak: 06:30 - 09:00
        # Afternoon slump: 14:00 - 17:00
        if 6 <= hour <= 9:
            return 0.85  # High success probability
        elif 14 <= hour <= 17:
            return 0.35  # High fatigue / low success probability
        else:
            return 0.55  # Medium success probability

    def calculate_fatigue_index(self) -> float:
        """
        Calculate a continuous fatigue score (0.0 = fully recovered, 1.0 = severe fatigue)
        based on focus session completion, missed wake-ups, and recent quest momentum.
        """
        try:
            database_manager.ensure_ready()
            
            # 1. Focus session failure rate (45% weight)
            focus_rows = database_manager.fetch_all(
                "SELECT completed FROM focus_sessions ORDER BY id DESC LIMIT 14"
            )
            if focus_rows:
                aborted = sum(1 for r in focus_rows if r["completed"] == 0)
                focus_fail_rate = aborted / len(focus_rows)
            else:
                focus_fail_rate = 0.5  # Neutral default

            # 2. Missed wake-up factor (35% weight)
            player_state = database_manager.fetch_one("SELECT missed_wake_ups FROM player_state WHERE id = 1")
            missed_wake_ups = player_state["missed_wake_ups"] if player_state else 0
            if missed_wake_ups == 0:
                wakeup_factor = 0.0
            elif missed_wake_ups == 1:
                wakeup_factor = 0.4
            elif missed_wake_ups == 2:
                wakeup_factor = 0.75
            else:
                wakeup_factor = 1.0

            # 3. Quest completion momentum (20% weight)
            progress_rows = database_manager.fetch_all(
                "SELECT status FROM quest_progress ORDER BY id DESC LIMIT 14"
            )
            if progress_rows:
                incomplete = sum(1 for r in progress_rows if r["status"] != "completed")
                quest_fail_rate = incomplete / len(progress_rows)
            else:
                quest_fail_rate = 0.5

            fatigue = (focus_fail_rate * 0.45) + (wakeup_factor * 0.35) + (quest_fail_rate * 0.20)
            return round(max(0.0, min(1.0, float(fatigue))), 2)
        except Exception as e:
            print(f"[Predictive Engine] Fatigue calculation error: {e}")
            return 0.50

    def get_operational_mode(
        self, 
        fatigue_index: float | None = None, 
        streak: int | None = None,
        missed_wake_ups: int | None = None,
    ) -> str:
        """
        Determine daily operational mode:
        - 'ACTIVE_RECOVERY': High fatigue (>=0.65) or >=2 missed wake-ups. Scales quests down to preserve streaks.
        - 'OVERDRIVE': Low fatigue (<0.25) and solid streak (>=5). Increases intensity and XP multiplier.
        - 'BALANCED': Standard discipline load.
        """
        try:
            if fatigue_index is None:
                fatigue_index = self.calculate_fatigue_index()
                
            database_manager.ensure_ready()
            player_state = database_manager.fetch_one("SELECT streak, missed_wake_ups FROM player_state WHERE id = 1")
            
            if streak is None:
                streak = player_state["streak"] if player_state else 0
            if missed_wake_ups is None:
                missed_wake_ups = player_state["missed_wake_ups"] if player_state else 0

            if fatigue_index >= 0.65 or missed_wake_ups >= 2:
                return "ACTIVE_RECOVERY"
            elif fatigue_index < 0.25 and streak >= 5:
                return "OVERDRIVE"
            else:
                return "BALANCED"
        except Exception as e:
            print(f"[Predictive Engine] Operational mode error: {e}")
            return "BALANCED"

    def get_circadian_peak_and_slump(self, weekday: int | None = None) -> dict[str, str]:
        """
        Scan probability curve between 06:00 and 22:00 to detect peak 2-hour focus window
        and lowest-energy 3-hour slump window.
        """
        if weekday is None:
            weekday = datetime.now().weekday()

        hourly_probs = []
        for h in range(6, 23):
            prob = self.predict_focus_success_probability(h, weekday)
            hourly_probs.append((h, prob))

        # Peak: find 2-hour rolling sum maximum
        best_peak_sum = -1.0
        peak_start = 8
        for i in range(len(hourly_probs) - 1):
            two_hour_sum = hourly_probs[i][1] + hourly_probs[i + 1][1]
            if two_hour_sum > best_peak_sum:
                best_peak_sum = two_hour_sum
                peak_start = hourly_probs[i][0]

        # Slump: find 3-hour rolling sum minimum
        best_slump_sum = 999.0
        slump_start = 14
        for i in range(len(hourly_probs) - 2):
            three_hour_sum = hourly_probs[i][1] + hourly_probs[i + 1][1] + hourly_probs[i + 2][1]
            if three_hour_sum < best_slump_sum:
                best_slump_sum = three_hour_sum
                slump_start = hourly_probs[i][0]

        return {
            "peak_start": f"{peak_start:02d}:00",
            "peak_end": f"{(peak_start + 2) % 24:02d}:00",
            "slump_start": f"{slump_start:02d}:00",
            "slump_end": f"{(slump_start + 3) % 24:02d}:00",
        }

# Global reusable instance
predictive_engine = PredictiveEngine()
