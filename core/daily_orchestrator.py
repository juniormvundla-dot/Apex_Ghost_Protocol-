from __future__ import annotations

# Orchestrates the full daily Apex Ghost loop:
# awakening (optional) -> daily quests -> coach feedback -> quest completion -> private mode

from dataclasses import dataclass
from datetime import date

from automation.awakening import MorningAwakeningProtocol
from automation.private_mode import PrivateModeController
from core.config import config
from quests.models import QuestStatus
from quests.service import quest_service
from quests.xp import xp_system
from storage.db import database_manager


@dataclass
class DailyRunResult:
    quests: list
    coach_feedback: object
    entered_private_mode: bool
    ran_intelligence_brief: bool


class DailyOrchestrator:
    """
    Runs the integrated daily workflow for Apex Ghost.
    """

    def __init__(self) -> None:
        database_manager.ensure_ready()
        self.awakening = MorningAwakeningProtocol(
            vlc_path=config.awakening.vlc_path,
        )
        self.private_mode = PrivateModeController(
            intellij_path=config.private_mode.intellij_path,
            browser_tabs=config.private_mode.browser_tabs,
            launch_intellij=config.private_mode.launch_intellij,
            launch_browser=config.private_mode.launch_browser,
            play_voice_greeting=config.private_mode.play_voice_greeting,
        )

    def run(self) -> DailyRunResult:
        print("\n==============================")
        print("APEX GHOST - DAILY PROTOCOL")
        print("==============================")

        missed_wake_up = self._maybe_run_awakening()
        xp_system.mark_active_day(date.today())

        snapshot = quest_service.build_progress_snapshot(missed_wake_up=missed_wake_up)
        coach_feedback = quest_service.get_coach_feedback(snapshot, snapshot.current_progress)
        snapshot.adjusted_difficulty = coach_feedback.adjusted_difficulty

        quests = quest_service.ensure_today_quests(snapshot)
        quest_service.print_daily_brief(quests, coach_feedback)

        if config.daily_flow.interactive_quest_completion:
            self._interactive_quest_loop(quests)

        entered_private_mode = False
        if config.daily_flow.offer_private_mode:
            entered_private_mode = self._maybe_enter_private_mode()

        ran_intelligence_brief = False
        if config.daily_flow.offer_intelligence_brief:
            ran_intelligence_brief = self._maybe_run_intelligence_brief()

        print("\nDaily protocol complete.")
        return DailyRunResult(
            quests=quests,
            coach_feedback=coach_feedback,
            entered_private_mode=entered_private_mode,
            ran_intelligence_brief=ran_intelligence_brief,
        )

    def _maybe_run_awakening(self) -> bool:
        if not config.awakening.run_on_daily_start:
            return False

        if config.awakening.skip_if_already_ran and self.awakening.already_ran_today():
            print("\nAwakening already completed today. Skipping video sequence.")
            return False

        choice = input("\nRun Morning Awakening now? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            self.awakening.run()
            return False

        if choice in ("n", "no"):
            xp_system.record_missed_wake_up()
            print("Awakening skipped. Coach will factor this into tomorrow's difficulty.")
            return True

        print("Invalid input. Skipping awakening.")
        xp_system.record_missed_wake_up()
        return True

    def _interactive_quest_loop(self, quests: list) -> None:
        pending = [quest for quest in quests if quest.status == QuestStatus.PENDING]

        while pending:
            print("\n--- Complete a quest ---")
            for index, quest in enumerate(pending, start=1):
                print(f"{index}. {quest.description}")

            choice = input(
                "Enter quest number to complete, or press Enter to continue: "
            ).strip()
            if not choice:
                break

            if not choice.isdigit():
                print("Invalid input.")
                continue

            selected_index = int(choice) - 1
            if selected_index < 0 or selected_index >= len(pending):
                print("Quest number out of range.")
                continue

            quest = pending[selected_index]
            quest_service.start_quest(quest)
            quest_service.complete_quest(quest)
            print(f"Completed: {quest.description} (+{quest.xp_reward} XP)")
            pending = [q for q in pending if q.status == QuestStatus.PENDING]

    def _maybe_enter_private_mode(self) -> bool:
        choice = input("\nEnter Private Mode now? [y/N]: ").strip().lower()
        if choice in ("y", "yes"):
            self.private_mode.enter_private_mode()
            return True
        return False

    def _maybe_run_intelligence_brief(self) -> bool:
        choice = input("\nRun Intelligence Brief now? [y/N]: ").strip().lower()
        if choice in ("y", "yes"):
            from scrapers.intelligence_service import run_intelligence_brief

            run_intelligence_brief()
            return True
        return False


def run_daily_protocol() -> DailyRunResult:
    """
    Convenience entry point for the daily workflow.
    """
    orchestrator = DailyOrchestrator()
    return orchestrator.run()
