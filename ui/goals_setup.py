from __future__ import annotations

# Interactive wizard for setting yearly goals and viewing the execution plan.

from datetime import date

from quests.goal_manager import goal_manager
from quests.goal_planner import goal_planner
from quests.goals import GOAL_CATEGORIES, GoalsConfig, HunterProfile, YearlyGoal


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def _prompt_int(text: str, default: int, minimum: int, maximum: int) -> int:
    while True:
        raw = _prompt(text, str(default))
        if not raw.isdigit():
            print("Please enter a number.")
            continue

        value = int(raw)
        if value < minimum or value > maximum:
            print(f"Enter a value between {minimum} and {maximum}.")
            continue
        return value


def _prompt_date(text: str, default: date) -> date:
    while True:
        raw = _prompt(text, default.isoformat())
        try:
            parsed = date.fromisoformat(raw)
        except ValueError:
            print("Use YYYY-MM-DD format.")
            continue

        if parsed <= date.today():
            print("Deadline must be in the future.")
            continue
        return parsed


def _prompt_yes_no(text: str, default_yes: bool = True) -> bool:
    default = "Y/n" if default_yes else "y/N"
    choice = input(f"{text} [{default}]: ").strip().lower()
    if not choice:
        return default_yes
    return choice in ("y", "yes")


def _print_categories() -> None:
    print("\nCategories:")
    for index, category in enumerate(GOAL_CATEGORIES, start=1):
        print(f"{index}. {category}")


def _choose_category() -> str:
    _print_categories()
    while True:
        raw = input("Choose category number: ").strip()
        if not raw.isdigit():
            print("Enter a category number.")
            continue

        index = int(raw) - 1
        if index < 0 or index >= len(GOAL_CATEGORIES):
            print("Category number out of range.")
            continue
        return GOAL_CATEGORIES[index]


def _collect_goal(existing: GoalsConfig | None = None) -> YearlyGoal | None:
    print("\n--- New Yearly Goal ---")
    title = _prompt("Goal title")
    if not title:
        print("Goal title is required.")
        return None

    category = _choose_category()
    description = _prompt("Describe why this goal matters")
    success_metric = _prompt("Success metric (how you'll know it's done)")
    deadline = _prompt_date(
        "Deadline (YYYY-MM-DD)",
        date(date.today().year, 12, 31),
    )
    priority = _prompt_int("Priority (1=highest, 5=lowest)", 2, 1, 5)

    goal = YearlyGoal(
        id=goal_manager.slugify(title),
        title=title,
        category=category,
        description=description,
        success_metric=success_metric,
        deadline=deadline,
        priority=priority,
    )
    goal_manager.decompose_goal(goal)

    print("\nAuto-generated execution layers:")
    print("Quarterly milestones:")
    for milestone in goal.milestones:
        print(f"  - {milestone}")
    print("Monthly focus:")
    for item in goal.monthly_focus:
        print(f"  - {item}")
    print("Weekly targets:")
    for item in goal.weekly_targets:
        print(f"  - {item}")
    print("Daily habits:")
    for item in goal.daily_habits:
        print(f"  - {item}")

    if _prompt_yes_no("Customize weekly/daily actions now?", default_yes=False):
        weekly = _prompt("Weekly targets (comma-separated)", ", ".join(goal.weekly_targets))
        daily = _prompt("Daily habits (comma-separated)", ", ".join(goal.daily_habits))
        goal.weekly_targets = [part.strip() for part in weekly.split(",") if part.strip()]
        goal.daily_habits = [part.strip() for part in daily.split(",") if part.strip()]

    issues = goal_manager.validate_goal(goal)
    if issues:
        print("\nGoal validation issues:")
        for issue in issues:
            print(f"- {issue}")
        if not _prompt_yes_no("Save anyway?", default_yes=False):
            return None

    if existing:
        for index, current in enumerate(existing.goals):
            if current.id == goal.id:
                existing.goals[index] = goal
                return goal

    return goal


def run_goals_wizard() -> GoalsConfig:
    """
    Walk through profile + yearly goals setup and save the execution plan.
    """
    print("\n==============================")
    print("APEX GHOST - GOAL SETUP")
    print("==============================")

    existing = goal_manager.load()
    if existing.goals:
        print(f"\nFound {len(existing.goals)} existing goal(s).")
        if not _prompt_yes_no("Replace all goals and start fresh?", default_yes=False):
            config = existing
        else:
            config = GoalsConfig(profile=existing.profile, goals=[])
    else:
        config = GoalsConfig()

    print("\n--- Hunter Profile ---")
    config.profile.hunter_name = _prompt("Your hunter name", config.profile.hunter_name)
    config.profile.year = _prompt_int(
        "Target year",
        config.profile.year or date.today().year,
        date.today().year,
        date.today().year + 5,
    )
    config.profile.north_star = _prompt(
        "North star (one sentence for the year)",
        config.profile.north_star,
    )

    if not config.goals:
        while True:
            goal = _collect_goal(config)
            if goal:
                config.goals.append(goal)

            if not _prompt_yes_no("Add another yearly goal?", default_yes=True):
                break

    for goal in config.goals:
        goal_manager.decompose_goal(goal)

    goal_manager.save(config)
    goal_manager.sync_quest_tree(config)
    plan = goal_planner.build_plan(config)
    goal_planner.print_plan(plan)

    print(f"\nGoals saved to: {goal_manager.goals_path}")
    print("Quest tree synced to database.")
    return config


def view_execution_plan() -> None:
    """
    Show the current execution plan from saved goals.
    """
    config = goal_manager.load()
    if not config.goals:
        print("\nNo yearly goals found.")
        print("Run goal setup first from the main menu.")
        return

    plan = goal_planner.build_plan(config)
    goal_planner.print_plan(plan)


def add_or_update_goal() -> None:
    """
    Add a new goal or update an existing one without wiping the full config.
    """
    config = goal_manager.load()
    goal = _collect_goal(config)
    if goal is None:
        return

    replaced = False
    for index, current in enumerate(config.goals):
        if current.id == goal.id:
            config.goals[index] = goal
            replaced = True
            break

    if not replaced:
        config.goals.append(goal)

    goal_manager.save(config)
    goal_manager.sync_quest_tree(config)
    goal_planner.print_plan(goal_planner.build_plan(config))
    print(f"\nGoals saved to: {goal_manager.goals_path}")
