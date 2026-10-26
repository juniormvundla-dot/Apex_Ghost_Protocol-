from __future__ import annotations

import json
from datetime import datetime
from storage.db import database_manager
from quests.predictive_engine import predictive_engine
from automation.ollama_client import ollama_client

class ShadowDirector:
    """
    The Shadow AI Director — The living, learning game director for Apex Ghost.
    Observes quest patterns, circadian rhythms, journal entries, and focus states
    to craft personalized, diegetic directives that mirror the System in Solo Leveling.
    """

    def get_shadow_state(self) -> dict:
        database_manager.ensure_ready()
        fatigue = predictive_engine.calculate_fatigue_index()
        circadian = predictive_engine.get_circadian_peak_and_slump()

        player_state = database_manager.fetch_one(
            "SELECT streak, missed_wake_ups, total_xp, rank FROM player_state WHERE id = 1"
        )
        streak = player_state["streak"] if player_state else 0
        missed_wake_ups = player_state["missed_wake_ups"] if player_state else 0
        rank = player_state["rank"] if player_state else "E"

        # Determine Shadow Operational Mode
        if fatigue >= 0.65 or missed_wake_ups >= 2:
            mode = "GUARDIAN"
            mode_desc = "Fatigue detected. Shielding streak with high-efficiency recovery."
        elif streak >= 7 and fatigue < 0.35:
            mode = "SCULPTOR"
            mode_desc = "Peak momentum. Escalating trials to forge high-rank discipline."
        elif streak == 0 or missed_wake_ups >= 1:
            mode = "AWAKENER"
            mode_desc = "Slump trajectory detected. Minimizing friction to re-establish identity."
        else:
            mode = "BALANCED"
            mode_desc = "Standard tactical surveillance. Sustained focus protocol."

        # Fetch latest active directive
        latest_row = database_manager.fetch_one(
            "SELECT message, directive_type, created_at FROM shadow_directives ORDER BY id DESC LIMIT 1"
        )
        if not latest_row:
            default_msg = self.generate_directive(mode, streak, fatigue, circadian)
            message = default_msg
        else:
            message = latest_row["message"]

        return {
            "mode": mode,
            "mode_desc": mode_desc,
            "fatigue_index": fatigue,
            "peak_window": f"{circadian['peak_start']} - {circadian['peak_end']}",
            "slump_window": f"{circadian['slump_start']} - {circadian['slump_end']}",
            "streak": streak,
            "rank": rank,
            "message": message
        }

    def generate_directive(self, mode: str | None = None, streak: int = 0, fatigue: float = 0.5, circadian: dict | None = None) -> str:
        database_manager.ensure_ready()

        if mode is None:
            state = self.get_shadow_state()
            mode = state["mode"]
            streak = state["streak"]
            fatigue = state["fatigue_index"]

        if circadian is None:
            circadian = predictive_engine.get_circadian_peak_and_slump()

        # Query recent completed vs missed stream distribution
        recent_quests = database_manager.fetch_all(
            "SELECT stream, status FROM quests ORDER BY id DESC LIMIT 15"
        )
        stream_counts = {}
        for q in recent_quests:
            s = q["stream"] or "WARRIOR"
            stream_counts[s] = stream_counts.get(s, 0) + 1

        top_stream = max(stream_counts, key=stream_counts.get) if stream_counts else "WARRIOR"

        # Try LLM generation first if Ollama is connected
        if ollama_client.check_connection():
            try:
                system_prompt = (
                    "You are The Shadow — the diegetic, sentient System Director from Solo Leveling. "
                    "You observe the Hunter's real life actions. You are stoic, hyper-perceptive, and razor-sharp. "
                    "Speak directly to the Hunter in exactly ONE concise sentence (max 25 words). "
                    "No conversational filler, no polite greetings. Make them feel observed and understood."
                )
                user_prompt = (
                    f"Hunter metrics:\n"
                    f"- Mode: {mode}\n"
                    f"- Streak: {streak} days\n"
                    f"- Fatigue: {int(fatigue * 100)}%\n"
                    f"- Peak focus window: {circadian['peak_start']} to {circadian['peak_end']}\n"
                    f"- Dominant stream: {top_stream}\n"
                    f"Synthesize the morning directive."
                )
                response = ollama_client.query(user_prompt, system_prompt)
                if response and len(response.strip()) > 10:
                    clean_msg = response.strip().replace('"', '').strip()
                    self._persist_directive(clean_msg, mode)
                    return clean_msg
            except Exception:
                pass

        # Intelligent deterministic fallback
        fallbacks = {
            "SCULPTOR": [
                f"Your {top_stream} discipline is compounding. Strike during your {circadian['peak_start']} window before complacency takes root.",
                f"Seven days of unbroken execution. The System is raising your trial difficulty today.",
                f"Momentum is your armor. Channel peak focus at {circadian['peak_start']} and push beyond your threshold."
            ],
            "GUARDIAN": [
                f"Fatigue index is at {int(fatigue * 100)}%. Protect your streak with clean execution, not reckless exhaustion.",
                f"Neural stamina is degraded. Execute your core objective before the {circadian['slump_start']} slump.",
                "Discipline is knowing when to retreat into active recovery so tomorrow's strike hits true."
            ],
            "AWAKENER": [
                "The streak broken is a lesson, not an identity. Clear one single non-negotiable contract today.",
                "Hesitation breeds friction. Execute the first task immediately and reset the trajectory.",
                "The System does not negotiate with excuses. Reclaim your rank with action."
            ],
            "BALANCED": [
                f"Surveillance active. Peak execution window opens at {circadian['peak_start']}.",
                f"Your actions in the {top_stream} domain speak clearly. Remain consistent today.",
                "Steady discipline forges monarchs. Focus on today's contracts without distraction."
            ]
        }

        import random
        chosen = random.choice(fallbacks.get(mode, fallbacks["BALANCED"]))
        self._persist_directive(chosen, mode)
        return chosen

    def _persist_directive(self, message: str, directive_type: str) -> None:
        database_manager.execute(
            """
            INSERT INTO shadow_directives (message, directive_type, created_at, is_active)
            VALUES (?, ?, datetime('now'), 1)
            """,
            (message, directive_type)
        )

shadow_director = ShadowDirector()
