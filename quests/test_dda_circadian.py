from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from quests.models import QuestCategory, QuestStatus
from quests.predictive_engine import predictive_engine
from quests.circadian_optimizer import circadian_optimizer
from quests.daily_generator import DailyQuestGenerator, ProgressSnapshot


def test_fatigue_and_operational_modes() -> None:
    print("\n--- Test 1: Fatigue Index & Operational Modes ---")
    fatigue = predictive_engine.calculate_fatigue_index()
    print(f"Calculated live database fatigue index: {fatigue} ({int(fatigue * 100)}%)")
    assert 0.0 <= fatigue <= 1.0, f"Fatigue index {fatigue} is out of bounds [0.0, 1.0]"

    # Test mode transitions
    mode_rec = predictive_engine.get_operational_mode(fatigue_index=0.75, streak=1, missed_wake_ups=0)
    print(f"High fatigue (0.75) mode: {mode_rec}")
    assert mode_rec == "ACTIVE_RECOVERY", f"Expected ACTIVE_RECOVERY, got {mode_rec}"

    mode_rec_wake = predictive_engine.get_operational_mode(fatigue_index=0.30, streak=4, missed_wake_ups=2)
    print(f"Missed wakeups (2) mode: {mode_rec_wake}")
    assert mode_rec_wake == "ACTIVE_RECOVERY", f"Expected ACTIVE_RECOVERY, got {mode_rec_wake}"

    mode_overdrive = predictive_engine.get_operational_mode(fatigue_index=0.15, streak=7, missed_wake_ups=0)
    print(f"Low fatigue (0.15), streak 7 mode: {mode_overdrive}")
    assert mode_overdrive == "OVERDRIVE", f"Expected OVERDRIVE, got {mode_overdrive}"

    mode_balanced = predictive_engine.get_operational_mode(fatigue_index=0.40, streak=2, missed_wake_ups=0)
    print(f"Medium fatigue (0.40) mode: {mode_balanced}")
    assert mode_balanced == "BALANCED", f"Expected BALANCED, got {mode_balanced}"
    print("[OK] Test 1 passed successfully.")


def test_context_aware_circadian_slots() -> None:
    print("\n--- Test 2: Context-Aware Circadian Slotting ---")
    
    # 1. Wakeup quest must anchor in the morning
    wakeup_slot = circadian_optimizer.get_time_recommendation(
        difficulty=1, category="CORE", context_hint="WAKEUP"
    )
    print(f"Wake-up slot recommendation: {wakeup_slot}")
    assert "Morning Anchor" in wakeup_slot or "05:00" in wakeup_slot, f"Wake-up slot unexpected: {wakeup_slot}"
    assert "Slump" not in wakeup_slot, f"Wake-up quest was erroneously slotted into slump: {wakeup_slot}"

    # 2. Deep work / Boss quest must target peak flow
    deep_work_slot = circadian_optimizer.get_time_recommendation(
        difficulty=4, category="BOSS", context_hint="DEEP_WORK"
    )
    print(f"Deep work / Boss slot: {deep_work_slot}")
    assert "Peak" in deep_work_slot, f"Expected Peak in deep work slot: {deep_work_slot}"

    # 3. Reading / Recovery must absorb slump
    recovery_slot = circadian_optimizer.get_time_recommendation(
        difficulty=1, category="SIDE", context_hint="RECOVERY"
    )
    print(f"Recovery / Reading slot: {recovery_slot}")
    assert "Slump" in recovery_slot, f"Expected Slump in recovery slot: {recovery_slot}"

    # 4. Maintenance / Admin midday
    maint_slot = circadian_optimizer.get_time_recommendation(
        difficulty=2, category="CORE", context_hint="MAINTENANCE"
    )
    print(f"Maintenance slot: {maint_slot}")
    assert "Midday Focus" in maint_slot or "11:00" in maint_slot, f"Expected Midday Focus: {maint_slot}"
    print("[OK] Test passed successfully.")


def test_dda_quest_generation_active_recovery() -> None:
    print("\n--- Test 3: DDA Active Recovery Quest Generation ---")
    generator = DailyQuestGenerator()
    
    snapshot_recovery = ProgressSnapshot(
        current_progress=30,
        previous_day_completion=30,
        streak=3,
        weak_day=True,
        missed_wake_up=True,
        adjusted_difficulty=1,
        fatigue_index=0.75,
        operational_mode="ACTIVE_RECOVERY",
    )

    quests = generator.generate_daily_quests(snapshot_recovery, target_date=date.today())
    print(f"Generated {len(quests)} quests in ACTIVE_RECOVERY mode:")
    for q in quests:
        print(f"  - [{q.category.value.upper()}] {q.title} | Diff: {q.difficulty} | XP: {q.xp_reward}")

    # Assertions
    titles = [q.title for q in quests]
    descriptions = [q.description for q in quests]
    
    # Check that wakeup is morning anchored
    wakeup_quest = [q for q in quests if "wake" in q.description.lower()][0]
    assert "Morning Anchor" in wakeup_quest.description, f"Wakeup quest not morning anchored: {wakeup_quest.description}"

    # Check that Boss quests were scaled down
    boss_quests = [q for q in quests if q.category == QuestCategory.BOSS]
    assert len(boss_quests) >= 1, "Expected at least 1 Boss quest"
    for b in boss_quests:
        assert b.difficulty <= 3, f"Boss quest difficulty too high for recovery mode: {b.difficulty}"
        assert b.evidence_required is False, f"Recovery Boss quest should not mandate anti-cheat: {b}"

    # Check focused sprint Pomodoro exists
    assert any("25-minute" in d or "Sprint" in d for d in descriptions), "Expected 25-min Pomodoro sprint in recovery mode"
    print("[OK] Test 3 passed successfully.")


def test_dda_quest_generation_overdrive() -> None:
    print("\n--- Test 4: DDA Overdrive Quest Generation ---")
    generator = DailyQuestGenerator()
    
    snapshot_overdrive = ProgressSnapshot(
        current_progress=95,
        previous_day_completion=100,
        streak=8,
        weak_day=False,
        missed_wake_up=False,
        adjusted_difficulty=3,
        fatigue_index=0.10,
        operational_mode="OVERDRIVE",
    )

    quests = generator.generate_daily_quests(snapshot_overdrive, target_date=date.today())
    print(f"Generated {len(quests)} quests in OVERDRIVE mode:")
    for q in quests:
        print(f"  - [{q.category.value.upper()}] {q.title} | Diff: {q.difficulty} | XP: {q.xp_reward}")

    # In Overdrive with streak > 7, there should be an elite streak challenge
    streak_boss = [q for q in quests if "[STREAK]" in q.description]
    assert len(streak_boss) == 1, "Expected [STREAK] Boss Level Challenge in Overdrive mode with streak > 7"
    assert streak_boss[0].xp_reward >= 300, "Expected high XP reward for streak boss"
    print("[OK] Test 4 passed successfully.")


if __name__ == "__main__":
    print("==================================================")
    print("APEX GHOST — DDA & CIRCADIAN TEST SUITE")
    print("==================================================")
    test_fatigue_and_operational_modes()
    test_context_aware_circadian_slots()
    test_dda_quest_generation_active_recovery()
    test_dda_quest_generation_overdrive()
    print("\n==================================================")
    print("ALL TESTS PASSED WITH ZERO ERRORS.")
    print("==================================================")
