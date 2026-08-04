from __future__ import annotations

# This file handles discipline and penalties for missed quests.
# The goal is not just punishment, but correction:
# - identify what was missed
# - store a penalty record
# - suggest a corrective action
# Later, this can trigger voice messages, reminders, or stricter actions.

from dataclasses import dataclass, field
from datetime import datetime

from quests.models import Quest, QuestStatus


@dataclass
class PenaltyRecord:
    """
    Represents a penalty applied because a quest was missed.
    """
    quest_title: str
    reason: str
    corrective_action: str
    timestamp: datetime = field(default_factory=datetime.now)


class PenaltyManager:
    """
    Manages penalties for missed or failed quests.
    """
    def __init__(self) -> None:
        self.records: list[PenaltyRecord] = []

    def apply_penalty(
            self,
            quest: Quest,
            reason: str,
            corrective_action: str,
    ) -> PenaltyRecord:
        """
        Apply a penalty to a quest and store it.
        """
        quest.miss()

        record = PenaltyRecord(
            quest_title=quest.title,
            reason=reason,
            corrective_action=corrective_action,
        )
        self.records.append(record)
        return record

    def apply_default_missed_penalty(self, quest: Quest) -> PenaltyRecord:
        """
        Apply a default penalty when a quest is missed.
        """
        return self.apply_penalty(
            quest=quest,
            reason="Daily quest was not completed before the deadline.",
            corrective_action="Review the missed task and schedule a recovery block.",
        )

    def total_penalties(self) -> int:
        """
        Return the number of penalties that have been recorded.
        """
        return len(self.records)

    def recent_penalties(self, limit: int = 10) -> list[PenaltyRecord]:
        """
        Return the most recent penalties.
        """
        return self.records[-limit:]

    def print_penalty_summary(self) -> None:
        """
        Print a simple summary of penalties.
        """
        print("\n=== PENALTY SUMMARY ===")
        print(f"Total penalties: {self.total_penalties()}")

        if not self.records:
            print("No penalties recorded.")
            return

        latest = self.records[-1]
        print(f"Latest penalty quest: {latest.quest_title}")
        print(f"Reason: {latest.reason}")
        print(f"Corrective action: {latest.corrective_action}")
        print(f"Timestamp: {latest.timestamp}")