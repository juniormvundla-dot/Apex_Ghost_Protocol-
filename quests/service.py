from __future__ import annotations

# This file provides a service layer for the quest system.
# A service sits above the raw models and repositories.
# It helps coordinate actions like:
# - creating quests
# - starting quests
# - completing quests
# - marking quests as missed
# - saving progress and penalties

from datetime import date

from quests.coach import AICoach, CoachFeedback, CoachInput
from quests.daily_generator import DailyQuestGenerator, ProgressSnapshot
from quests.goal_planner import goal_planner
from quests.models import Quest, QuestCategory, QuestLevel, QuestStatus
from quests.progress import ProgressTracker
from quests.penalties import PenaltyManager
from quests.xp import xp_system
from storage.repositories import quest_repository, progress_repository, penalty_repository


class QuestService:
    """
    High-level service for working with quests.

    This class makes it easier for the rest of the system to work with quests
    without needing to know database details.
    """

    def __init__(
        self,
        tracker: ProgressTracker | None = None,
        penalty_manager: PenaltyManager | None = None,
        daily_generator: DailyQuestGenerator | None = None,
        coach: AICoach | None = None,
    ) -> None:
        self.tracker = tracker or ProgressTracker()
        self.penalty_manager = penalty_manager or PenaltyManager()
        self.daily_generator = daily_generator or DailyQuestGenerator()
        self.coach = coach or AICoach()

    def create_quest(
        self,
        title: str,
        description: str,
        level: QuestLevel,
        target_date: date | None = None,
        notes: str = "",
    ) -> Quest:
        """
        Create a new quest and save it to the database.
        """
        quest = Quest(
            title=title,
            description=description,
            level=level,
            target_date=target_date,
            notes=notes,
        )
        quest_repository.save_quest(quest)
        return quest

    def start_quest(self, quest: Quest) -> Quest:
        """
        Mark a quest as started and store the progress event.
        """
        self.tracker.record_started(quest, notes="Quest started.")
        progress_repository.save_progress(self.tracker.records[-1])
        quest_repository.save_quest(quest)
        return quest

    def complete_quest_with_evidence(self, quest: Quest, evidence: str) -> bool:
        """
        Validate evidence using local LLM before completing the quest.
        Returns True if accepted, False if rejected.
        """
        if quest.evidence_required:
            from automation.ollama_client import ollama_client
            
            if ollama_client.check_connection():
                prompt = (
                    f"The user claims to have completed the quest '{quest.title}'.\n"
                    f"Quest Description: {quest.description}\n"
                    f"Provided Evidence: {evidence}\n\n"
                    f"Does this evidence reasonably prove the user completed the task? "
                    f"If yes, reply with 'ACCEPTED'. If it is lazy, fake, or insufficient, reply with 'REJECTED'."
                )
                system = "You are J.A.R.V.I.S., an anti-cheat validation AI. Be strict. Only output ACCEPTED or REJECTED."
                response = ollama_client.query(prompt, system)
                
                if response and "REJECTED" in response.upper():
                    print(f"[Evidence Rejected] {quest.title}: {evidence}")
                    return False
                    
        quest.evidence_submitted = evidence
        self.complete_quest(quest, notes=f"Evidence provided: {evidence}")
        return True

    def complete_quest(self, quest: Quest, notes: str = "Quest completed.") -> Quest:
        """
        Mark a quest as completed and store the progress event.
        """
        self.tracker.record_completion(quest, notes=notes)
        progress_repository.save_progress(self.tracker.records[-1])
        quest_repository.save_quest(quest)

        if quest.category in (QuestCategory.CORE, QuestCategory.BOSS):
            xp_system.add_xp(quest.xp_reward)

        return quest

    def miss_quest(
        self,
        quest: Quest,
        reason: str = "Quest missed before deadline.",
        corrective_action: str = "Review the task and schedule a recovery block.",
    ) -> Quest:
        """
        Mark a quest as missed and store the penalty and progress event.
        """
        self.tracker.record_missed(quest, notes=reason)
        progress_repository.save_progress(self.tracker.records[-1])

        penalty = self.penalty_manager.apply_penalty(
            quest=quest,
            reason=reason,
            corrective_action=corrective_action,
        )
        penalty_repository.save_penalty(penalty)

        if quest.penalty_xp > 0:
            xp_system.apply_penalty(quest.penalty_xp)

        quest_repository.save_quest(quest)
        return quest

    def create_daily_quest(
        self,
        title: str,
        description: str,
        target_date: date | None = None,
        notes: str = "",
    ) -> Quest:
        """
        Convenience method for creating a daily quest.
        """
        return self.create_quest(
            title=title,
            description=description,
            level=QuestLevel.DAILY,
            target_date=target_date,
            notes=notes,
        )

    def get_all_quests(self) -> list[Quest]:
        """
        Load all quests from storage.
        """
        return quest_repository.get_all_quests()

    def get_active_quests(self) -> list[Quest]:
        """
        Load all quests that are currently in progress.
        """
        return quest_repository.find_by_status(QuestStatus.IN_PROGRESS)

    def get_pending_quests(self) -> list[Quest]:
        """
        Load all quests that are still pending.
        """
        return quest_repository.find_by_status(QuestStatus.PENDING)

    def get_completed_quests(self) -> list[Quest]:
        """
        Load all completed quests.
        """
        return quest_repository.find_by_status(QuestStatus.COMPLETED)

    def get_today_daily_quests(self, target_date: date | None = None) -> list[Quest]:
        """
        Load daily quests for the given date.
        """
        target_date = target_date or date.today()
        return quest_repository.find_daily_by_date(target_date)

    def ensure_today_quests(
        self,
        snapshot: ProgressSnapshot,
        target_date: date | None = None,
    ) -> list[Quest]:
        """
        Return today's daily quests, generating and saving them if needed.
        """
        target_date = target_date or date.today()
        existing = self.get_today_daily_quests(target_date)
        if existing:
            return existing

        generated = self.daily_generator.generate_daily_quests(
            snapshot,
            target_date,
            goal_actions=goal_planner.get_current_plan(target_date).today_actions,
        )
        for quest in generated:
            quest_repository.save_quest(quest)
        return generated

    def build_progress_snapshot(
        self,
        adjusted_difficulty: int = 2,
        missed_wake_up: bool = False,
    ) -> ProgressSnapshot:
        """
        Build a snapshot from stored XP and recent quest progress.
        """
        xp_summary = xp_system.get_summary()
        recent = progress_repository.get_recent_progress(limit=20)
        completed = sum(1 for record in recent if record.status == QuestStatus.COMPLETED)
        total = len(recent) or 1
        completion_rate = int((completed / total) * 100)

        return ProgressSnapshot(
            current_progress=completion_rate,
            previous_day_completion=completion_rate,
            streak=int(xp_summary["streak"]),
            weak_day=completion_rate < 50,
            missed_wake_up=missed_wake_up,
            adjusted_difficulty=adjusted_difficulty,
        )

    def get_coach_feedback(
        self,
        snapshot: ProgressSnapshot,
        completion_rate: float,
    ) -> CoachFeedback:
        """
        Run the coach analysis for the current day.
        """
        xp_summary = xp_system.get_summary()
        return self.coach.analyze(
            CoachInput(
                missed_wake_ups=int(xp_summary["missed_wake_ups"]),
                performance_trend=0.0,
                streak=int(xp_summary["streak"]),
                hard_tasks_avoided=0,
                completion_rate=completion_rate,
            )
        )

    def print_daily_brief(
        self,
        quests: list[Quest],
        coach_feedback: CoachFeedback,
    ) -> None:
        """
        Print today's quests, XP status, and coach feedback.
        """
        xp_summary = xp_system.get_summary()
        plan = goal_planner.get_current_plan()

        if plan.north_star:
            print(f"\nNorth Star: {plan.north_star}")

        if plan.today_actions:
            print("\n--- GOAL-LINKED FOCUS ---")
            for action in plan.today_actions:
                print(f"- {action}")

        print("\n=== TODAY'S QUESTS ===")
        for index, quest in enumerate(quests, start=1):
            print(
                f"{index}. [{quest.category.value.upper()}] {quest.description} "
                f"(Diff {quest.difficulty}, XP {quest.xp_reward}, "
                f"Status {quest.status.value})"
            )

        print("\n=== HUNTER STATUS ===")
        print(f"Total XP: {xp_summary['total_xp']}")
        print(f"Rank: {xp_summary['rank']}")
        print(f"Streak: {xp_summary['streak']} days")

        print("\n=== COACH FEEDBACK ===")
        if coach_feedback.warnings:
            for warning in coach_feedback.warnings:
                print(f"- Warning: {warning}")
        for recommendation in coach_feedback.recommendations:
            print(f"- Recommendation: {recommendation}")
        print(f"- Adjusted difficulty for tomorrow: {coach_feedback.adjusted_difficulty}")

    def print_progress_summary(self) -> None:
        """
        Print a quick summary of quest progress and penalties.
        """
        self.tracker.print_summary()
        self.penalty_manager.print_penalty_summary()


# Reusable service instance.
quest_service = QuestService()