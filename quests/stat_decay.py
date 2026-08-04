import os
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent

from storage.db import database_manager
from quests.models import QuestStatus

class StatDecaySystem:
    """
    Deducts attribute points (STR, INT, AGI, DIS) if relevant quest categories 
    have not been completed within a 4-day grace window.
    """
    def __init__(self):
        self.decay_threshold_days = 4

    def check_and_apply_decay(self):
        """
        Check completed quests in the database and calculate decays.
        """
        try:
            database_manager.ensure_ready()
            # Get current date
            today = date.today()
            
            # Load current attributes
            attr_row = database_manager.fetch_one("SELECT * FROM player_attributes WHERE id = 1")
            if not attr_row:
                return
            
            str_val = attr_row["strength"]
            int_val = attr_row["intelligence"]
            agi_val = attr_row["agility"]
            dis_val = attr_row["discipline"]
            last_check_str = attr_row["last_decay_check"]

            # Prevent duplicate daily decay calculations
            if last_check_str == today.isoformat():
                return attr_row

            # Fetch all completed quests
            completed_rows = database_manager.fetch_all(
                "SELECT title, target_date, category FROM quests WHERE status = ?",
                (QuestStatus.COMPLETED.value,)
            )

            # Map categories to last completed dates
            last_dates = {
                "physical": None,     # STR
                "intellect": None,    # INT
                "agility": None,      # AGI
                "discipline": None    # DIS
            }

            for row in completed_rows:
                title = row["title"].lower()
                target_date_str = row["target_date"]
                category = row["category"]
                
                try:
                    q_date = date.fromisoformat(target_date_str)
                except:
                    continue

                # Heuristic mapping title/category to attributes
                is_physical = any(w in title for w in ["gym", "workout", "training", "mobility", "fitness", "run", "stretch"])
                is_intellect = any(w in title for w in ["read", "learn", "study", "review", "research"])
                is_agility = any(w in title for w in ["refactor", "algorithm", "speed", "test"])
                
                if is_physical:
                    if not last_dates["physical"] or q_date > last_dates["physical"]:
                        last_dates["physical"] = q_date
                elif is_intellect:
                    if not last_dates["intellect"] or q_date > last_dates["intellect"]:
                        last_dates["intellect"] = q_date
                elif is_agility:
                    if not last_dates["agility"] or q_date > last_dates["agility"]:
                        last_dates["agility"] = q_date
                else:
                    if not last_dates["discipline"] or q_date > last_dates["discipline"]:
                        last_dates["discipline"] = q_date

            # Calculate decay amounts
            decay_applied = False
            decay_log = []
            
            for attr_key, last_date in last_dates.items():
                if last_date:
                    days_elapsed = (today - last_date).days
                else:
                    # No completed quest in this category, start counting from 5 days ago to trigger decay warning
                    days_elapsed = 5

                if days_elapsed >= self.decay_threshold_days:
                    decay_amount = days_elapsed - self.decay_threshold_days + 1
                    
                    if attr_key == "physical" and str_val > 1:
                        str_val = max(1, str_val - decay_amount)
                        decay_log.append(f"Strength decayed by {decay_amount} (Last action: {days_elapsed} days ago)")
                        decay_applied = True
                    elif attr_key == "intellect" and int_val > 1:
                        int_val = max(1, int_val - decay_amount)
                        decay_log.append(f"Intelligence decayed by {decay_amount} (Last action: {days_elapsed} days ago)")
                        decay_applied = True
                    elif attr_key == "agility" and agi_val > 1:
                        agi_val = max(1, agi_val - decay_amount)
                        decay_log.append(f"Agility decayed by {decay_amount} (Last action: {days_elapsed} days ago)")
                        decay_applied = True
                    elif attr_key == "discipline" and dis_val > 1:
                        dis_val = max(1, dis_val - decay_amount)
                        decay_log.append(f"Discipline decayed by {decay_amount} (Last action: {days_elapsed} days ago)")
                        decay_applied = True

            # If stats have decayed significantly, spawn a Recovery Quest automatically
            if decay_applied:
                for log in decay_log:
                    print(f"[Skills Decay] {log}")
                
                # Update attributes
                database_manager.execute(
                    """
                    UPDATE player_attributes 
                    SET strength = ?, intelligence = ?, agility = ?, discipline = ?, last_decay_check = ?
                    WHERE id = 1
                    """,
                    (str_val, int_val, agi_val, dis_val, today.isoformat())
                )

                # Check if high-stakes Recovery Quest is already active
                recovery_exists = database_manager.fetch_one(
                    "SELECT 1 FROM quests WHERE title LIKE '%[RECOVERY]%' AND status = 'PENDING'"
                )
                if not recovery_exists:
                    # Spawn high-stakes quest to reclaim lost stat points!
                    database_manager.execute(
                        """
                        INSERT OR IGNORE INTO quests (title, description, level, status, target_date, category, difficulty, xp_reward, penalty_xp)
                        VALUES (?, ?, 'daily', 'pending', ?, 'boss', 5, 250, 100)
                        """,
                        (
                            "[RECOVERY] Reclaim Attribute Synergy",
                            "Complete double deep-work sessions or training block to restore all decayed base statistics.",
                            today.isoformat()
                        )
                    )
                    print("[Skills Decay] Spawned Attribute Recovery Quest.")

            return {
                "strength": str_val,
                "intelligence": int_val,
                "agility": agi_val,
                "discipline": dis_val
            }
        except Exception as e:
            print(f"[Skills Decay Error] {e}")
            return None

# Global stat decay system instance
stat_decay_system = StatDecaySystem()
