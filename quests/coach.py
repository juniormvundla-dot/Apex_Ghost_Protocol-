from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CoachFeedback:
    warnings: list[str]
    recommendations: list[str]
    adjusted_difficulty: int


@dataclass
class CoachInput:
    missed_wake_ups: int
    performance_trend: float
    streak: int
    hard_tasks_avoided: int
    completion_rate: float


class AICoach:
    """
    Rule-based coach for discipline analysis.
    """

    def analyze(self, data: CoachInput) -> CoachFeedback:
        warnings: list[str] = []
        recommendations: list[str] = []
        adjusted_difficulty = 2

        if data.missed_wake_ups > 0:
            warnings.append("Wake-up consistency is slipping.")
            recommendations.append("Fix the morning anchor before increasing workload.")
            adjusted_difficulty = 1

        if data.performance_trend < 0:
            warnings.append("Performance is declining.")
            recommendations.append("Reduce overload and focus on high-quality execution.")
            adjusted_difficulty = max(1, adjusted_difficulty - 1)

        if data.hard_tasks_avoided >= 2:
            warnings.append("You are avoiding difficult tasks.")
            recommendations.append("Start the hardest task first tomorrow.")
            adjusted_difficulty = min(5, adjusted_difficulty + 1)

        if data.completion_rate >= 85 and data.streak >= 7:
            recommendations.append("You are in a strong zone. Increase challenge slightly.")
            adjusted_difficulty = min(5, adjusted_difficulty + 1)

        if not warnings:
            recommendations.append("Good consistency. Keep the current rhythm.")

        return CoachFeedback(
            warnings=warnings,
            recommendations=recommendations,
            adjusted_difficulty=adjusted_difficulty,
        )
