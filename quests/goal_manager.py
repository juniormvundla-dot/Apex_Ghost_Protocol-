from __future__ import annotations

import json
import re
from datetime import date, timedelta

from core.paths import paths
from quests.goals import GOAL_CATEGORIES, GoalsConfig, HunterProfile, YearlyGoal
from quests.models import Quest, QuestCategory, QuestLevel, QuestNode
from quests.quest_tree import QuestTree
from storage.repositories import quest_repository


CATEGORY_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "monthly": [
            "Build consistent training rhythm",
            "Improve strength and body composition markers",
        ],
        "weekly": [
            "Complete 4 disciplined training sessions",
            "Track nutrition and recovery basics",
        ],
        "daily": [
            "Perform one training or mobility block",
            "Hit daily movement minimum (steps or active minutes)",
        ],
    },
    "career": {
        "monthly": [
            "Ship one meaningful project milestone",
            "Deepen core technical skills",
        ],
        "weekly": [
            "Complete 5 deep work sessions",
            "Deliver one visible career output",
        ],
        "daily": [
            "90-minute focused build or study session",
            "Review tomorrow's top priority task",
        ],
    },
    "learning": {
        "monthly": [
            "Master one focused learning topic",
            "Apply learning through a small project or notes",
        ],
        "weekly": [
            "Complete 3 learning blocks",
            "Summarize key insights from the week",
        ],
        "daily": [
            "45-minute deliberate learning block",
            "Capture one insight in notes",
        ],
    },
    "discipline": {
        "monthly": [
            "Maintain wake-up consistency above 85%",
            "Reduce distraction windows during work blocks",
        ],
        "weekly": [
            "Wake on time at least 6 days",
            "Complete all core daily quests at least 5 days",
        ],
        "daily": [
            "Wake up on time and start without delay",
            "Finish the hardest task before optional tasks",
        ],
    },
    "finance": {
        "monthly": [
            "Track spending and stay within budget",
            "Increase savings or debt payoff progress",
        ],
        "weekly": [
            "Review accounts and upcoming expenses",
            "Make one intentional money decision",
        ],
        "daily": [
            "Log one expense or financial action",
            "Avoid one impulsive purchase trigger",
        ],
    },
    "personal": {
        "monthly": [
            "Invest in one relationship or personal growth area",
            "Protect recovery and mental reset time",
        ],
        "weekly": [
            "Schedule one meaningful personal block",
            "Complete one maintenance or life-admin task",
        ],
        "daily": [
            "10-minute reflection or journaling block",
            "One small action that supports balance",
        ],
    },
    "custom": {
        "monthly": ["Define one monthly milestone for this goal"],
        "weekly": ["Define one weekly action for this goal"],
        "daily": ["Define one daily habit for this goal"],
    },
}


class GoalManager:
    """
    Loads yearly goals, decomposes them, and syncs them into the quest tree.
    """

    def __init__(self) -> None:
        self.goals_path = paths.core_dir / "yearly_goals.json"

    def load(self) -> GoalsConfig:
        if not self.goals_path.exists():
            return GoalsConfig()

        data = json.loads(self.goals_path.read_text(encoding="utf-8"))
        profile_data = data.get("profile", {})
        profile = HunterProfile(
            hunter_name=profile_data.get("hunter_name", "Hunter"),
            year=profile_data.get("year", date.today().year),
            north_star=profile_data.get("north_star", ""),
        )

        goals: list[YearlyGoal] = []
        for item in data.get("goals", []):
            goals.append(
                YearlyGoal(
                    id=item["id"],
                    title=item["title"],
                    category=item.get("category", "custom"),
                    description=item.get("description", ""),
                    success_metric=item.get("success_metric", ""),
                    deadline=date.fromisoformat(item["deadline"]),
                    priority=int(item.get("priority", 3)),
                    milestones=list(item.get("milestones", [])),
                    monthly_focus=list(item.get("monthly_focus", [])),
                    weekly_targets=list(item.get("weekly_targets", [])),
                    daily_habits=list(item.get("daily_habits", [])),
                )
            )

        config = GoalsConfig(profile=profile, goals=goals)
        for goal in config.goals:
            self.decompose_goal(goal)
        return config

    def save(self, config: GoalsConfig) -> None:
        payload = {
            "profile": {
                "hunter_name": config.profile.hunter_name,
                "year": config.profile.year,
                "north_star": config.profile.north_star,
            },
            "goals": [
                {
                    "id": goal.id,
                    "title": goal.title,
                    "category": goal.category,
                    "description": goal.description,
                    "success_metric": goal.success_metric,
                    "deadline": goal.deadline.isoformat(),
                    "priority": goal.priority,
                    "milestones": goal.milestones,
                    "monthly_focus": goal.monthly_focus,
                    "weekly_targets": goal.weekly_targets,
                    "daily_habits": goal.daily_habits,
                }
                for goal in config.goals
            ],
        }
        self.goals_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def slugify(self, text: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        return slug or "goal"

    def decompose_goal(self, goal: YearlyGoal) -> YearlyGoal:
        """
        Fill missing execution layers using category templates and milestones.
        """
        template = CATEGORY_TEMPLATES.get(goal.category, CATEGORY_TEMPLATES["custom"])

        if not goal.milestones:
            goal.milestones = self._generate_quarterly_milestones(goal)

        if not goal.monthly_focus:
            goal.monthly_focus = [
                f"{goal.title}: {item}" for item in template["monthly"]
            ]

        if not goal.weekly_targets:
            goal.weekly_targets = [
                f"{goal.title}: {item}" for item in template["weekly"]
            ]

        if not goal.daily_habits:
            goal.daily_habits = [
                f"{goal.title}: {item}" for item in template["daily"]
            ]

        return goal

    def _generate_quarterly_milestones(self, goal: YearlyGoal) -> list[str]:
        today = date.today()
        year = goal.deadline.year
        quarter_ends = [
            (date(year, 3, 31), "Q1 foundation"),
            (date(year, 6, 30), "Q2 momentum"),
            (date(year, 9, 30), "Q3 acceleration"),
            (goal.deadline, "Q4 completion"),
        ]

        milestones: list[str] = []
        for quarter_end, label in quarter_ends:
            if quarter_end >= today:
                milestones.append(
                    f"{label}: advance '{goal.title}' toward {goal.success_metric}"
                )
        return milestones[:4]

    def validate_goal(self, goal: YearlyGoal) -> list[str]:
        issues: list[str] = []

        if not goal.title.strip():
            issues.append("Goal title is required.")
        if goal.category not in GOAL_CATEGORIES:
            issues.append(f"Category must be one of: {', '.join(GOAL_CATEGORIES)}")
        if not goal.success_metric.strip():
            issues.append("Success metric is required so progress can be measured.")
        if goal.deadline <= date.today():
            issues.append("Deadline must be in the future.")
        if goal.priority < 1 or goal.priority > 5:
            issues.append("Priority must be between 1 (highest) and 5 (lowest).")

        return issues

    def build_quest_tree(self, config: GoalsConfig) -> QuestTree:
        """
        Convert yearly goals into a hierarchical quest tree.
        """
        tree = QuestTree()

        if not config.goals:
            return tree

        if len(config.goals) == 1:
            root_goal = config.goals[0]
        else:
            root_goal = YearlyGoal(
                id="annual-mission",
                title=config.profile.north_star or f"{config.profile.year} Annual Mission",
                category="discipline",
                description="Combined annual mission across all active goals.",
                success_metric="Complete all priority goals for the year.",
                deadline=max(goal.deadline for goal in config.goals),
                priority=1,
            )

        root_quest = self._goal_to_quest(root_goal, QuestLevel.ANNUAL)
        root_node = tree.set_root(root_quest)

        for goal in sorted(config.goals, key=lambda item: item.priority):
            annual_node = (
                root_node
                if len(config.goals) == 1
                else tree.add_child(
                    root_node,
                    self._goal_to_quest(goal, QuestLevel.ANNUAL),
                )
            )

            month_end = self._month_end(date.today())
            month_quest = Quest(
                title=f"[MONTHLY] {goal.title} ({month_end.strftime('%Y-%m')})",
                description=goal.monthly_focus[0] if goal.monthly_focus else goal.title,
                level=QuestLevel.MONTHLY,
                target_date=month_end,
                notes=f"goal_id={goal.id}",
            )
            month_node = tree.add_child(annual_node, month_quest)

            week_end = self._week_end(date.today())
            week_quest = Quest(
                title=f"[WEEKLY] {goal.title} ({week_end.isoformat()})",
                description=goal.weekly_targets[0] if goal.weekly_targets else goal.title,
                level=QuestLevel.WEEKLY,
                target_date=week_end,
                notes=f"goal_id={goal.id}",
            )
            tree.add_child(month_node, week_quest)

        return tree

    def sync_quest_tree(self, config: GoalsConfig) -> QuestTree:
        """
        Persist the current goal hierarchy into the quest database.
        """
        tree = self.build_quest_tree(config)
        for node in tree.walk():
            quest_repository.save_quest(node.quest)
        return tree

    def _goal_to_quest(self, goal: YearlyGoal, level: QuestLevel) -> Quest:
        return Quest(
            title=f"[{level.value.upper()}] {goal.title}",
            description=goal.description or goal.success_metric,
            level=level,
            target_date=goal.deadline,
            notes=f"goal_id={goal.id}; metric={goal.success_metric}",
        )

    def _month_end(self, current: date) -> date:
        if current.month == 12:
            return current.replace(day=31)
        next_month = current.replace(month=current.month + 1, day=1)
        return next_month - timedelta(days=1)

    def _week_end(self, current: date) -> date:
        days_until_sunday = 6 - current.weekday()
        return current + timedelta(days=days_until_sunday)


goal_manager = GoalManager()
