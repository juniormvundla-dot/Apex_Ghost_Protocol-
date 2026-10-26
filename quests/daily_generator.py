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
    fatigue_index: float = 0.0
    operational_mode: str = "BALANCED"


class DailyQuestGenerator:
    """
    Generates daily quests based on progress, coach-adjusted difficulty,
    fatigue telemetry, and circadian performance slots.
    """

    def generate_daily_quests(
        self,
        snapshot: ProgressSnapshot,
        target_date: date | None = None,
        goal_actions: list[str] | None = None,
    ) -> list[Quest]:
        target_date = target_date or date.today()
        from quests.predictive_engine import predictive_engine
        from quests.circadian_optimizer import circadian_optimizer

        # Resolve active operational mode from telemetry
        op_mode = snapshot.operational_mode or predictive_engine.get_operational_mode(
            snapshot.fatigue_index, snapshot.streak
        )

        base_difficulty = snapshot.adjusted_difficulty or self._adaptive_difficulty(snapshot)
        quests: list[Quest] = []

        circadian_optimizer.calculate_profile()

        # ── 1. ACTIVE RECOVERY MODE (Protect Streaks & Prevent Burnout) ─────────
        if op_mode == "ACTIVE_RECOVERY":
            quest_templates = [
                (
                    QuestCategory.CORE,
                    "Active Recovery: Wake up gently and rehydrate without screen scrolling",
                    1,
                    80,
                    20,
                    False,
                    "WAKEUP",
                ),
                (
                    QuestCategory.CORE,
                    "Focused Sprint: 25-minute Pomodoro single-task block",
                    2,
                    90,
                    30,
                    False,
                    "DEEP_WORK",
                ),
                (
                    QuestCategory.BOSS,
                    "Active Recovery: Hit 130g Protein, hydrate 2.5L, and 20-min mobility walk",
                    2,
                    120,
                    40,
                    False,
                    "RECOVERY",
                ),
                (
                    QuestCategory.BOSS,
                    "Finance: Review and log today's expenses in ledger",
                    2,
                    100,
                    30,
                    False,
                    "MAINTENANCE",
                ),
                (
                    QuestCategory.SIDE,
                    "Active Recovery: Read 1 chapter or 15 minutes of quiet reflection",
                    1,
                    60,
                    0,
                    False,
                    "RECOVERY",
                ),
            ]

        # ── 2. OVERDRIVE MODE (Peak Performance & Bonus XP) ───────────────────
        elif op_mode == "OVERDRIVE":
            base_difficulty = min(5, base_difficulty + 1)
            quest_templates = [
                (
                    QuestCategory.CORE,
                    "Wake up at dawn anchor and initiate deep focus without delay",
                    base_difficulty,
                    140,
                    70,
                    False,
                    "WAKEUP",
                ),
            ]

            for index, action in enumerate(goal_actions or []):
                if index >= 3:
                    break
                quest_templates.append(
                    (
                        QuestCategory.CORE,
                        f"[OVERDRIVE] {action}",
                        base_difficulty,
                        160,
                        80,
                        False,
                        "MAINTENANCE",
                    )
                )

            quest_templates.extend(
                [
                    (
                        QuestCategory.CORE,
                        "Complete 90-minute unbroken high-intensity deep-work session",
                        base_difficulty + 1,
                        180,
                        90,
                        False,
                        "DEEP_WORK",
                    ),
                    (
                        QuestCategory.BOSS,
                        "Fitness: Hit 180g of Protein and 2900 kcal for 82kg Lean Bulk",
                        base_difficulty + 2,
                        260,
                        130,
                        True,
                        "DEEP_WORK",
                    ),
                    (
                        QuestCategory.BOSS,
                        "Finance: Audit expenses or set up 15% automatic deduction",
                        base_difficulty + 2,
                        260,
                        130,
                        True,
                        "MAINTENANCE",
                    ),
                    (
                        QuestCategory.SIDE,
                        "Finance: Read 1 chapter of 'The Psychology of Money'",
                        max(1, base_difficulty - 1),
                        120,
                        0,
                        False,
                        "RECOVERY",
                    ),
                ]
            )

        # ── 3. BALANCED MODE (Standard High-Discipline Protocol) ───────────────
        else:
            quest_templates = [
                (
                    QuestCategory.CORE,
                    "Wake up on time and start the day without delay",
                    base_difficulty,
                    100 + base_difficulty * 20,
                    50 + base_difficulty * 10,
                    False,
                    "WAKEUP",
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
                        False,
                        "MAINTENANCE",
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
                        False,
                        "DEEP_WORK",
                    ),
                    (
                        QuestCategory.BOSS,
                        "Fitness: Hit 180g of Protein and 2900 kcal for 82kg Lean Bulk",
                        base_difficulty + 2,
                        200,
                        100,
                        True,
                        "DEEP_WORK",
                    ),
                    (
                        QuestCategory.BOSS,
                        "Finance: Audit expenses or set up 15% automatic deduction",
                        base_difficulty + 2,
                        200,
                        100,
                        True,
                        "MAINTENANCE",
                    ),
                    (
                        QuestCategory.SIDE,
                        "Finance: Read 1 chapter of 'The Psychology of Money'",
                        max(1, base_difficulty - 1),
                        100,
                        0,
                        False,
                        "RECOVERY",
                    ),
                ]
            )

        # Build quests with context-aware circadian slots
        for item in quest_templates:
            category = item[0]
            description = item[1]
            difficulty = item[2]
            xp_reward = item[3]
            penalty_xp = item[4]
            evidence_required = item[5] if len(item) > 5 else False
            context_hint = item[6] if len(item) > 6 else None

            cat_str = category.value if hasattr(category, "value") else str(category)
            rec_slot = circadian_optimizer.get_time_recommendation(
                difficulty=difficulty, 
                category=cat_str, 
                context_hint=context_hint
            )
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

        if snapshot.streak > 7 and op_mode != "ACTIVE_RECOVERY":
            boss_slot = circadian_optimizer.get_time_recommendation(
                difficulty=5,
                category="BOSS",
                context_hint="DEEP_WORK"
            )
            quests.append(
                self._build_quest(
                    description=f"[{boss_slot}] [STREAK] Boss Level Challenge (7+ day streak)",
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
        
        # Intelligently assign stream domain based on quest content
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["fitness", "gym", "protein", "workout", "pushup", "run", "rehydrate", "walk"]):
            stream = "WARRIOR"
        elif any(w in desc_lower for w in ["finance", "audit", "expense", "budget", "money", "deduction"]):
            stream = "SOVEREIGN"
        elif any(w in desc_lower for w in ["code", "build", "project", "landing", "repo", "ship", "launch"]):
            stream = "ARCHITECT"
        elif any(w in desc_lower for w in ["read", "study", "learn", "chapter", "skill", "algorithm"]):
            stream = "SAGE"
        elif any(w in desc_lower for w in ["journal", "meditat", "mind", "shadow", "recon", "reflect"]):
            stream = "SHADOW"
        else:
            stream = "WARRIOR"

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
            stream=stream,
        )

    def _adaptive_difficulty(self, snapshot: ProgressSnapshot) -> int:
        difficulty = 2

        if snapshot.previous_day_completion >= 80:
            difficulty += 1
        if snapshot.streak >= 5:
            difficulty += 1
        if snapshot.weak_day or snapshot.missed_wake_up or snapshot.fatigue_index >= 0.65:
            difficulty = max(1, difficulty - 1)

        return max(1, min(difficulty, 5))
