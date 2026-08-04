from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from quests.models import Quest, QuestCategory, QuestLevel


@dataclass
class ProgressSnapshot:
    """
    Input for adaptive daily quest generation.
    """
    current_progress: int
    previous_day_completion: int
    streak: int
    weak_day: bool = False
    missed_wake_up: bool = False
    adjusted_difficulty: int = 2


class DailyQuestGenerator:
    """
    Generates daily quests based on progress and coach-adjusted difficulty.
    """

    def generate_daily_quests(
        self,
        snapshot: ProgressSnapshot,
        target_date: date | None = None,
        goal_actions: list[str] | None = None,
    ) -> list[Quest]:
        target_date = target_date or date.today()
        base_difficulty = snapshot.adjusted_difficulty or self._adaptive_difficulty(snapshot)
        quests: list[Quest] = []

        quest_templates = [
            (
                QuestCategory.CORE,
                "Wake up on time and start the day without delay",
                base_difficulty,
                100 + base_difficulty * 20,
                50 + base_difficulty * 10,
            ),
        ]

        for index, action in enumerate(goal_actions or []):
            if index >= 3:
                break
            quest_templates.append(
                (
                    QuestCategory.CORE,
                    action,
                    base_difficulty + 1,
                    120 + base_difficulty * 20,
                    60 + base_difficulty * 10,
                )
            )

        quest_templates.extend(
            [
                (
                    QuestCategory.CORE,
                    "Complete one focused deep-work session",
                    base_difficulty + 1,
                    120 + base_difficulty * 25,
                    60 + base_difficulty * 10,
                    False
                ),
                (
                    QuestCategory.BOSS,
                    "Fitness: Hit 180g of Protein and 2900 kcal for 82kg Lean Bulk",
                    base_difficulty + 2,
                    200,
                    100,
                    True
                ),
                (
                    QuestCategory.BOSS,
                    "Finance: Audit expenses or set up 15% automatic deduction",
                    base_difficulty + 2,
                    200,
                    100,
                    True
                ),
                (
                    QuestCategory.SIDE,
                    "Finance: Read 1 chapter of 'The Psychology of Money'",
                    max(1, base_difficulty - 1),
                    100,
                    0,
                    False
                ),
            ]
        )

        from quests.circadian_optimizer import circadian_optimizer
        circadian_optimizer.calculate_profile()

        for item in quest_templates:
            category = item[0]
            description = item[1]
            difficulty = item[2]
            xp_reward = item[3]
            penalty_xp = item[4]
            evidence_required = item[5] if len(item) > 5 else False

            rec_slot = circadian_optimizer.get_time_recommendation(difficulty, category.value if hasattr(category, "value") else str(category))
            opt_description = f"[{rec_slot}] {description}"
            quests.append(
                self._build_quest(
                    description=opt_description,
                    category=category,
                    difficulty=difficulty,
                    xp_reward=xp_reward,
                    penalty_xp=penalty_xp,
                    target_date=target_date,
                    evidence_required=evidence_required,
                )
            )

        if snapshot.streak > 7:
            quests.append(
                self._build_quest(
                    description="[STREAK] Boss Level Challenge (7+ day streak)",
                    category=QuestCategory.BOSS,
                    difficulty=5,
                    xp_reward=300 + (snapshot.streak * 10),
                    penalty_xp=150,
                    target_date=target_date,
                    evidence_required=True,
                )
            )

        return quests

    def _build_quest(
        self,
        description: str,
        category: QuestCategory,
        difficulty: int,
        xp_reward: int,
        penalty_xp: int,
        target_date: date,
        evidence_required: bool = False,
    ) -> Quest:
        title = f"[{category.value.upper()}] {description} ({target_date.isoformat()})"
        return Quest(
            title=title,
            description=description,
            level=QuestLevel.DAILY,
            target_date=target_date,
            category=category,
            difficulty=difficulty,
            xp_reward=xp_reward,
            penalty_xp=penalty_xp,
            evidence_required=evidence_required,
        )

    def _adaptive_difficulty(self, snapshot: ProgressSnapshot) -> int:
        difficulty = 2

        if snapshot.previous_day_completion >= 80:
            difficulty += 1
        if snapshot.streak >= 5:
            difficulty += 1
        if snapshot.weak_day or snapshot.missed_wake_up:
            difficulty = max(1, difficulty - 1)

        return max(1, min(difficulty, 5))
