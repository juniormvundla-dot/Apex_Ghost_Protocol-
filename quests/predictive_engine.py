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

# Global reusable instance
predictive_engine = PredictiveEngine()
