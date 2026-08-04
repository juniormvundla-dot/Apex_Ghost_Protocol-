from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


GOAL_CATEGORIES = [
    "fitness",
    "career",
    "learning",
    "discipline",
    "finance",
    "personal",
    "custom",
]


@dataclass
class YearlyGoal:
    """
    One annual objective with measurable outcomes and execution layers.
    """
    id: str
    title: str
    category: str
    description: str
    success_metric: str
    deadline: date
    priority: int = 3
    milestones: list[str] = field(default_factory=list)
    monthly_focus: list[str] = field(default_factory=list)
    weekly_targets: list[str] = field(default_factory=list)
    daily_habits: list[str] = field(default_factory=list)


@dataclass
class HunterProfile:
    """
    Identity and direction for the year.
    """
    hunter_name: str = "Hunter"
    year: int = date.today().year
    north_star: str = ""


@dataclass
class GoalsConfig:
    """
    Full yearly goal configuration stored on disk.
    """
    profile: HunterProfile = field(default_factory=HunterProfile)
    goals: list[YearlyGoal] = field(default_factory=list)
