from __future__ import annotations

# This file tracks progress across quests.
# It helps the system know what has been completed, missed, or is still pending.
# Later, this can be connected to a database for permanent storage.

from dataclasses import dataclass, field
from datetime import datetime

from quests.models import Quest, QuestStatus


@dataclass
class QuestProgressRecord:
    """
    Stores a single progress event for a quest.
    """
    quest_title: str
    status: QuestStatus
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class ProgressTracker:
    """
    Tracks progress for quests over time.

    This is a lightweight v1 tracker.
    Later we can connect it to persistent storage.
    """
    records: list[QuestProgressRecord] = field(default_factory=list)

    def record_started(self, quest: Quest, notes: str = "") -> None:
        """
        Record that a quest was started.
        """
        quest.start()
        self.records.append(
            QuestProgressRecord(
                quest_title=quest.title,
                status=QuestStatus.IN_PROGRESS,
                notes=notes,
            )
        )

    def record_completion(self, quest: Quest, notes: str = "") -> None:
        """
        Record that a quest was completed.
        """
        quest.complete()
        self.records.append(
            QuestProgressRecord(
                quest_title=quest.title,
                status=QuestStatus.COMPLETED,
                notes=notes,
            )
        )

    def record_missed(self, quest: Quest, notes: str = "") -> None:
        """
        Record that a quest was missed.
        """
        quest.miss()
        self.records.append(
            QuestProgressRecord(
                quest_title=quest.title,
                status=QuestStatus.MISSED,
                notes=notes,
            )
        )

    def get_quest_status(self, quest: Quest) -> QuestStatus:
        """
        Returns the latest recorded status of a quest.
        """
        for record in reversed(self.records):
            if record.quest_title == quest.title:
                return record.status
        return QuestStatus.PENDING

    def total_records(self) -> int:
        """
        Return the total number of progress records.
        """
        return len(self.records)

    def completed_count(self) -> int:
        """
        Return the number of completed quest records.
        """
        return sum(1 for record in self.records if record.status == QuestStatus.COMPLETED)

    def missed_count(self) -> int:
        """
        Return the number of missed quest records.
        """
        return sum(1 for record in self.records if record.status == QuestStatus.MISSED)

    def completion_rate(self) -> float:
        """
        Return a completion percentage based on recorded events.
        """
        total = self.total_records()
        if total == 0:
            return 0.0
        return (self.completed_count() / total) * 100.0

    def recent_records(self, limit: int = 10) -> list[QuestProgressRecord]:
        """
        Return the most recent progress records.
        """
        return self.records[-limit:]

    def print_summary(self) -> None:
        """
        Print a quick progress summary to the console.
        """
        print("\n=== QUEST PROGRESS SUMMARY ===")
        print(f"Total records: {self.total_records()}")
        print(f"Completed: {self.completed_count()}")
        print(f"Missed: {self.missed_count()}")
        print(f"Completion rate: {self.completion_rate():.2f}%")