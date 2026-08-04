from __future__ import annotations

# This file controls "Private Mode" for Apex Ghost.
# Private Mode is the focused work environment you want to activate
# when you are ready to work seriously.
#
# For v1, this module can:
# - launch IntelliJ IDEA
# - open a browser with useful tabs
# - play a voice greeting
# - print status messages so you know what happened
#
# It uses system_control.py for lower-level actions.

from dataclasses import dataclass

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import datetime
from automation.system_control import system_controller
from core.config import config
from voice.jinwoo_voice import play_private_mode_greeting, generate_greeting
from quests.xp import xp_system
from quests.goal_manager import goal_manager
from quests.service import quest_service
from quests.models import QuestStatus
from storage.db import database_manager


@dataclass(frozen=True)
class PrivateModeSettings:
    """
    Configuration values for private mode.

    This keeps the behavior easy to change without editing the main logic.
    """
    launch_intellij: bool = True
    launch_browser: bool = True
    play_voice_greeting: bool = True


class PrivateModeController:
    """
    Controls the private/focus mode workflow.

    Responsibilities:
    - open IntelliJ IDEA
    - open important browser tabs
    - play a voice greeting
    - keep the logic clean and easy to expand
    """

    def __init__(
        self,
        settings: PrivateModeSettings | None = None,
        intellij_path: str | None = None,
        browser_tabs: list[str] | None = None,
        launch_intellij: bool | None = None,
        launch_browser: bool | None = None,
        play_voice_greeting: bool | None = None,
    ) -> None:
        base = settings or PrivateModeSettings()
        self.config = PrivateModeSettings(
            launch_intellij=launch_intellij if launch_intellij is not None else base.launch_intellij,
            launch_browser=launch_browser if launch_browser is not None else base.launch_browser,
            play_voice_greeting=(
                play_voice_greeting
                if play_voice_greeting is not None
                else base.play_voice_greeting
            ),
        )

        self.browser_tabs = browser_tabs or list(config.private_mode.browser_tabs)
        self.intellij_executable_path = (
            intellij_path or config.private_mode.intellij_path
        )
        from automation.focus_guard import FocusGuard
        self.focus_guard = FocusGuard()

    def launch_intellij(self) -> None:
        """
        Launch IntelliJ IDEA.
        """
        print("Launching IntelliJ IDEA...")

        if self.intellij_executable_path:
            system_controller.launch_app_by_path(self.intellij_executable_path)
            return

        print(
            "IntelliJ executable path is not set yet. "
            "Please add the exact IntelliJ path when ready."
        )

    def open_browser_tabs(self) -> None:
        """
        Open the browser tabs used for private mode.
        """
        print("Opening browser tabs...")
        system_controller.open_urls(self.browser_tabs)

    def play_greeting(self) -> None:
        """
        Play the private mode voice greeting.
        Database queries are performed on the main thread, and audio playback
        is offloaded to a background thread to prevent SQLite multithreading violations.
        """
        print("Playing private mode greeting...")
        try:
            summary = xp_system.get_summary()
            rank = summary.get("rank", "E")
            streak = summary.get("streak", 0)
            
            config_goals = goal_manager.load()
            hunter_name = config_goals.profile.hunter_name or "Hunter"
            north_star = config_goals.profile.north_star or ""
            
            pending_quests = len([
                q for q in quest_service.get_today_daily_quests() 
                if q.status == QuestStatus.PENDING
            ])
            
            greeting = None
            
            # Check local AI agent first (Offline Ollama RAG)
            from automation.ollama_client import ollama_client
            if ollama_client.check_connection():
                try:
                    from automation.rag_engine import rag_engine
                    context_docs = rag_engine.retrieve_context("focus session startup", limit=3)
                    context_str = "\n".join([doc["text"] for doc in context_docs])
                    
                    prompt = (
                        f"Briefing for Hunter {hunter_name} (Rank {rank}, Streak {streak} days).\n"
                        f"North Star: {north_star}\n"
                        f"Pending Quests: {pending_quests}\n"
                        f"Recent context:\n{context_str}\n\n"
                        f"Provide a sleek, J.A.R.V.I.S.-style greeting to initiate the focus block. Limit to 2-3 sentences. Encourage the hunter."
                    )
                    system_prompt = "You are J.A.R.V.I.S., a concise, sleek, intelligent developer assistant. Keep answers brief."
                    
                    print("[J.A.R.V.I.S.] Formulating custom RAG briefing...")
                    greeting = ollama_client.query(prompt, system_prompt)
                except Exception as ex:
                    print(f"[Ollama RAG Greeting Error] {ex}")

            if not greeting and getattr(config.private_mode, "use_gemini", False):
                from voice.jarvis_brain import generate_jarvis_briefing
                greeting = generate_jarvis_briefing(
                    hunter_name=hunter_name,
                    rank=rank,
                    streak=streak,
                    north_star=north_star,
                    pending_quests=pending_quests
                )
                
            if not greeting:
                greeting = generate_greeting(
                    hunter_name=hunter_name,
                    rank=rank,
                    streak=streak,
                    north_star=north_star,
                    pending_quests=pending_quests
                )
            
            import threading
            threading.Thread(
                target=play_private_mode_greeting,
                args=(greeting,),
                daemon=True
            ).start()
        except Exception as e:
            print(f"Failed to generate dynamic greeting: {e}. Falling back to default.")
            import threading
            threading.Thread(
                target=play_private_mode_greeting,
                daemon=True
            ).start()


    def start_session(self) -> int:
        """
        Record the start of a private mode focus session in the database.
        Returns the session ID.
        """
        try:
            from automation.soundscape_engine import soundscape_engine
            soundscape_engine.play_profile("focus_beats")
        except Exception as e:
            print(f"Error starting focus soundscape: {e}")

        database_manager.ensure_ready()
        now = datetime.datetime.now().isoformat()
        database_manager.execute(
            "INSERT INTO focus_sessions (start_time, completed) VALUES (?, 0)",
            (now,)
        )
        row = database_manager.fetch_one("SELECT last_insert_rowid() AS id")
        session_id = row["id"] if row else 0
        print(f"Focus session started. (ID: {session_id})")
        return session_id

    def end_session(self, session_id: int) -> None:
        """
        Record the end of a private mode focus session, calculate duration,
        and auto-complete the deep-work quest if the session was long enough.
        """
        try:
            from automation.soundscape_engine import soundscape_engine
            soundscape_engine.stop()
        except Exception as e:
            print(f"Error stopping focus soundscape: {e}")

        if not session_id:
            return

        now = datetime.datetime.now()
        row = database_manager.fetch_one(
            "SELECT start_time FROM focus_sessions WHERE id = ?",
            (session_id,)
        )
        if not row:
            print("Session not found in database.")
            return

        start_time_str = row["start_time"]
        start_time = datetime.datetime.fromisoformat(start_time_str)
        duration = now - start_time
        duration_minutes = int(duration.total_seconds() / 60)

        database_manager.execute(
            "UPDATE focus_sessions SET end_time = ?, completed = 1 WHERE id = ?",
            (now.isoformat(), session_id)
        )

        print(f"\nFocus session ended. Duration: {duration_minutes} minutes.")

        min_minutes = getattr(config.private_mode, "min_deep_work_minutes", 45)
        if duration_minutes >= min_minutes:
            print(f"Well done! You met the deep-work threshold of {min_minutes} minutes.")
            self._autocomplete_deep_work_quest(duration_minutes)
        else:
            print(f"Session was {duration_minutes} minutes. (Threshold: {min_minutes} minutes to clear Daily Quest).")

    def _autocomplete_deep_work_quest(self, duration_minutes: int) -> None:
        try:
            today_quests = quest_service.get_today_daily_quests()
            deep_work_quest = None
            for quest in today_quests:
                if quest.description == "Complete one focused deep-work session" and quest.status == QuestStatus.PENDING:
                    deep_work_quest = quest
                    break

            if deep_work_quest:
                quest_service.start_quest(deep_work_quest)
                quest_service.complete_quest(
                    deep_work_quest, 
                    notes=f"Completed focus session of {duration_minutes} minutes."
                )
                print(f"SUCCESS: Quest '{deep_work_quest.description}' auto-completed!")
            else:
                print("No pending deep-work quest found for today (already completed or not generated).")
        except Exception as e:
            print(f"Error completing deep-work quest: {e}")

    def enter_private_mode(self) -> None:
        """
        Run the full private mode workflow.
        """
        print("\n==============================")
        print("APEX GHOST - PRIVATE MODE")
        print("==============================")
        print("Activating focus environment...\n")

        if self.config.play_voice_greeting:
            self.play_greeting()

        if self.config.launch_browser:
            self.open_browser_tabs()

        if self.config.launch_intellij:
            self.launch_intellij()

        # Start distraction locking (Focus Guard)
        self.focus_guard.start_guard()

        print("\nPrivate Mode activated successfully.")

        # Start tracking session
        session_id = self.start_session()

        try:
            print("\n[FOCUS MODE ENGAGED]")
            print("Press Enter to exit Private Mode and log your session...")
            input()
        finally:
            # Stop distraction locking (guaranteed to run even on crash/Ctrl+C)
            self.focus_guard.stop_guard()

        self.end_session(session_id)


def activate_private_mode() -> None:
    """
    Convenience function so other files can start private mode easily.
    """
    controller = PrivateModeController()
    controller.enter_private_mode()


if __name__ == "__main__":
    activate_private_mode()