from __future__ import annotations

# This file defines the core data structures for the quest system.
# A quest is a unit of work or discipline in the Apex Ghost system.
# Examples:
# - Annual goal
# - Monthly theme
# - Weekly sprint
# - Daily quest

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class QuestLevel(str, Enum):
    """
    Quest levels represent the hierarchy of goals.

    LEVEL 4 = Annual goal
    LEVEL 3 = Monthly theme
    LEVEL 2 = Weekly sprint
    LEVEL 1 = Daily quest
    """
    ANNUAL = "annual"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


class QuestStatus(str, Enum):
    """
    Status of a quest in the system.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


class QuestCategory(str, Enum):
    """
    Daily quest categories used for XP and penalty rules.
    """
    CORE = "core"
    SIDE = "side"
    BOSS = "boss"


@dataclass
class Quest:
    """
    Represents one quest in the system.

    Fields:
    - title: short name of the quest
    - description: more detail about what the quest means
    - level: annual/monthly/weekly/daily
    - target_date: the date the quest is expected to be completed
    - completed_at: when it was actually completed
    - status: current state of the quest
    - notes: optional extra notes
    """
    title: str
    description: str
    level: QuestLevel
    target_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    status: QuestStatus = QuestStatus.PENDING
    notes: str = ""
    category: QuestCategory = QuestCategory.CORE
    difficulty: int = 2
    xp_reward: int = 100
    penalty_xp: int = 50
    evidence_required: bool = False
    evidence_submitted: str = ""

    def start(self) -> None:
        """
        Mark the quest as started.
        """
        if self.status == QuestStatus.PENDING:
            self.status = QuestStatus.IN_PROGRESS

    def complete(self) -> None:
        """
        Mark the quest as completed.
        """
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.now()

    def miss(self) -> None:
        """
        Mark the quest as missed.
        """
        self.status = QuestStatus.MISSED

    def is_completed(self) -> bool:
        """
        Return True if the quest is completed.
        """
        return self.status == QuestStatus.COMPLETED

    def is_missed(self) -> bool:
        """
        Return True if the quest is missed.
        """
        return self.status == QuestStatus.MISSED

    def is_active(self) -> bool:
        """
        Return True if the quest is currently in progress.
        """
        return self.status == QuestStatus.IN_PROGRESS


@dataclass
class QuestNode:
    """
    A quest node lets us build a tree structure.

    Each node can have:
    - one quest
    - child quests below it
    """
    quest: Quest
    children: list["QuestNode"] = field(default_factory=list)

    def add_child(self, child: "QuestNode") -> None:
        """
        Add a child quest below this quest.
        """
        self.children.append(child)

    def find_children_by_level(self, level: QuestLevel) -> list["QuestNode"]:
        """
        Return all direct child nodes with the given level.
        """
        return [child for child in self.children if child.quest.level == level]