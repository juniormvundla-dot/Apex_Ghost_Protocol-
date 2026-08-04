from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from quests.goal_manager import goal_manager
from quests.goals import GoalsConfig, YearlyGoal


@dataclass
class ExecutionPlan:
    """
    Current execution view derived from yearly goals.
    """
    profile_name: str
    north_star: str
    plan_date: date
    yearly_goals: list[YearlyGoal] = field(default_factory=list)
    monthly_focus: list[str] = field(default_factory=list)
    weekly_targets: list[str] = field(default_factory=list)
    today_actions: list[str] = field(default_factory=list)
    current_quarter: str = ""
    week_number: int = 1


class GoalPlanner:
    """
    Turns yearly goals into what to execute today, this week, and this month.
    """

    MAX_DAILY_GOAL_ACTIONS = 3

    def build_plan(self, config: GoalsConfig, plan_date: date | None = None) -> ExecutionPlan:
        plan_date = plan_date or date.today()
        sorted_goals = sorted(config.goals, key=lambda goal: goal.priority)

        monthly_focus = self._select_monthly_focus(sorted_goals, plan_date)
        weekly_targets = self._select_weekly_targets(sorted_goals, plan_date)
        today_actions = self._select_today_actions(sorted_goals, plan_date)

        return ExecutionPlan(
            profile_name=config.profile.hunter_name,
            north_star=config.profile.north_star,
            plan_date=plan_date,
            yearly_goals=sorted_goals,
            monthly_focus=monthly_focus,
            weekly_targets=weekly_targets,
            today_actions=today_actions,
            current_quarter=self._current_quarter(plan_date),
            week_number=plan_date.isocalendar().week,
        )

    def get_current_plan(self, plan_date: date | None = None) -> ExecutionPlan:
        config = goal_manager.load()
        return self.build_plan(config, plan_date)

    def print_plan(self, plan: ExecutionPlan) -> None:
        print("\n==============================")
        print("APEX GHOST - EXECUTION PLAN")
        print("==============================")
        print(f"Hunter: {plan.profile_name}")
        if plan.north_star:
            print(f"North Star: {plan.north_star}")
        print(f"Date: {plan.plan_date.isoformat()} | {plan.current_quarter} | Week {plan.week_number}")

        print("\n--- YEARLY GOALS ---")
        if not plan.yearly_goals:
            print("No yearly goals configured yet. Run goal setup first.")
            return

        for goal in plan.yearly_goals:
            print(
                f"- [P{goal.priority}] {goal.title} ({goal.category}) "
                f"-> {goal.success_metric} by {goal.deadline.isoformat()}"
            )

        print("\n--- THIS MONTH ---")
        for item in plan.monthly_focus:
            print(f"- {item}")

        print("\n--- THIS WEEK ---")
        for item in plan.weekly_targets:
            print(f"- {item}")

        print("\n--- TODAY ---")
        for item in plan.today_actions:
            print(f"- {item}")

        print("\n--- EXECUTION RULE ---")
        print("1. Protect the morning anchor (wake + first core quest)")
        print("2. Complete goal-linked actions before optional tasks")
        print("3. Enter Private Mode for deep work on career/build goals")
        print("4. Review misses at end of day and adjust tomorrow")

    def _select_monthly_focus(self, goals: list[YearlyGoal], plan_date: date) -> list[str]:
        month_index = min(max(plan_date.month - 1, 0), 11)
        focus: list[str] = []

        for goal in goals[:4]:
            if not goal.monthly_focus:
                continue
            item_index = month_index % len(goal.monthly_focus)
            focus.append(goal.monthly_focus[item_index])

        return focus

    def _select_weekly_targets(self, goals: list[YearlyGoal], plan_date: date) -> list[str]:
        week_index = plan_date.isocalendar().week
        targets: list[str] = []

        for goal in goals[:4]:
            if not goal.weekly_targets:
                continue
            item_index = week_index % len(goal.weekly_targets)
            targets.append(goal.weekly_targets[item_index])

        return targets

    def _select_today_actions(self, goals: list[YearlyGoal], plan_date: date) -> list[str]:
        weekday = plan_date.weekday()
        actions: list[str] = []

        for goal in goals:
            if not goal.daily_habits:
                continue

            habit_index = weekday % len(goal.daily_habits)
            actions.append(goal.daily_habits[habit_index])

            if len(actions) >= self.MAX_DAILY_GOAL_ACTIONS:
                break

        return actions

    def _current_quarter(self, plan_date: date) -> str:
        quarter = ((plan_date.month - 1) // 3) + 1
        return f"Q{quarter} {plan_date.year}"


goal_planner = GoalPlanner()
