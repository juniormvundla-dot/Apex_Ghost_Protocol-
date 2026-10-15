from __future__ import annotations

# APEX GHOST — MIDNIGHT ENFORCER
# ──────────────────────────────────────────────────────────────────────────────
# Runs at 23:45 every night (triggered by Windows Task Scheduler or the
# background scheduler daemon).
#
# Enforcement sequence:
#   1. Scan all PENDING/IN_PROGRESS CORE and BOSS quests for today
#   2. Apply XP penalties to each unfinished quest
#   3. Escalate based on consecutive miss streak:
#       Tier 1 (1st miss)  : XP penalty + J.A.R.V.I.S. callout + Recovery Quest spawned
#       Tier 2 (2nd miss)  : All of Tier 1 + Focus Guard activates (2-hour distraction block)
#       Tier 3 (3+ misses) : All of Tier 2 + Penalty Zone — machine hostile until
#                            mandatory accountability statement is submitted
#   4. Log enforcement action to DB for coach analysis
#   5. Save miss streak so escalation persists across days
# ──────────────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path
from datetime import date, datetime

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from storage.db import database_manager
from quests.models import QuestStatus, QuestCategory
from quests.xp import xp_system
from voice.tts import speak_text


class MidnightEnforcer:
    """
    The 23:45 enforcement engine.

    This is NOT a reminder. This is a consequence system.
    Every CORE and BOSS quest that is still PENDING at 23:45 is treated
    as a failure — with real, escalating consequences.
    """

    # ── ENFORCEMENT TIERS ─────────────────────────────────────────────────────
    TIER_1_THRESHOLD = 1   # 1st miss in sequence → soft enforcement
    TIER_2_THRESHOLD = 2   # 2nd consecutive miss → medium enforcement
    TIER_3_THRESHOLD = 3   # 3+ consecutive misses → hostile enforcement

    def __init__(self) -> None:
        database_manager.ensure_ready()
        self._ensure_miss_streak_table()

    def _ensure_miss_streak_table(self) -> None:
        """Create the enforcement tracking table if it doesn't exist."""
        database_manager.execute("""
            CREATE TABLE IF NOT EXISTS enforcement_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enforcement_date TEXT NOT NULL,
                missed_quest_title TEXT NOT NULL,
                tier INTEGER NOT NULL,
                xp_penalty INTEGER NOT NULL,
                action_taken TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        database_manager.execute("""
            CREATE TABLE IF NOT EXISTS miss_streak (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                consecutive_miss_days INTEGER NOT NULL DEFAULT 0,
                last_miss_date TEXT,
                accountability_due INTEGER NOT NULL DEFAULT 0
            )
        """)
        database_manager.execute(
            "INSERT OR IGNORE INTO miss_streak (id, consecutive_miss_days, last_miss_date, accountability_due) VALUES (1, 0, NULL, 0)"
        )

    # ── MISS STREAK TRACKING ──────────────────────────────────────────────────

    def _get_miss_streak(self) -> int:
        row = database_manager.fetch_one("SELECT consecutive_miss_days FROM miss_streak WHERE id = 1")
        return row["consecutive_miss_days"] if row else 0

    def _increment_miss_streak(self) -> int:
        """Increment miss streak and return the new value."""
        database_manager.execute(
            "UPDATE miss_streak SET consecutive_miss_days = consecutive_miss_days + 1, last_miss_date = ? WHERE id = 1",
            (date.today().isoformat(),)
        )
        return self._get_miss_streak()

    def _reset_miss_streak(self) -> None:
        """Reset miss streak when hunter clears all daily quests."""
        database_manager.execute(
            "UPDATE miss_streak SET consecutive_miss_days = 0, last_miss_date = NULL WHERE id = 1"
        )

    def _set_accountability_due(self, due: bool) -> None:
        database_manager.execute(
            "UPDATE miss_streak SET accountability_due = ? WHERE id = 1",
            (1 if due else 0,)
        )

    def accountability_is_due(self) -> bool:
        row = database_manager.fetch_one("SELECT accountability_due FROM miss_streak WHERE id = 1")
        return bool(row["accountability_due"]) if row else False

    # ── QUEST SCANNING ────────────────────────────────────────────────────────

    def _get_todays_pending_critical_quests(self) -> list[dict]:
        """
        Return all CORE and BOSS quests for today that are still PENDING or IN_PROGRESS.
        These are the quests that count against the hunter at midnight.
        """
        today = date.today().isoformat()
        rows = database_manager.fetch_all(
            """
            SELECT id, title, description, category, xp_reward, penalty_xp
            FROM quests
            WHERE target_date = ?
              AND category IN ('core', 'boss')
              AND status IN ('pending', 'in_progress')
            """,
            (today,)
        )
        return [dict(r) for r in rows]

    def _get_todays_completed_critical_quests(self) -> int:
        """Count how many CORE/BOSS quests were actually completed today."""
        today = date.today().isoformat()
        row = database_manager.fetch_one(
            """
            SELECT COUNT(*) as cnt FROM quests
            WHERE target_date = ? AND category IN ('core', 'boss') AND status = 'completed'
            """,
            (today,)
        )
        return row["cnt"] if row else 0

    # ── PENALTY APPLICATION ───────────────────────────────────────────────────

    def _apply_xp_penalty(self, quest: dict) -> int:
        """Apply XP penalty for a missed quest. Returns amount deducted."""
        penalty = quest.get("penalty_xp", 50)
        xp_system.apply_penalty(penalty)
        # Mark quest as missed in DB
        database_manager.execute(
            "UPDATE quests SET status = 'missed' WHERE id = ?",
            (quest["id"],)
        )
        return penalty

    def _spawn_recovery_quest(self, missed_titles: list[str]) -> None:
        """Spawn a high-stakes Recovery Quest if one doesn't already exist today."""
        today = date.today().isoformat()
        existing = database_manager.fetch_one(
            "SELECT 1 FROM quests WHERE title LIKE '%[RECOVERY]%' AND target_date = ? AND status = 'pending'",
            (today,)
        )
        if not existing:
            titles_str = ", ".join(missed_titles[:2])
            database_manager.execute(
                """
                INSERT OR IGNORE INTO quests
                (title, description, level, status, target_date, category, difficulty, xp_reward, penalty_xp, evidence_required)
                VALUES (?, ?, 'daily', 'pending', ?, 'boss', 5, 300, 150, 1)
                """,
                (
                    f"[RECOVERY] Reclaim the Day — {today}",
                    f"Complete a double deep-work session (90+ min verified) to restore lost XP from: {titles_str}. Evidence required.",
                    today,
                )
            )
            print("[Enforcer] Recovery Quest spawned for tomorrow.")

    def _log_enforcement(self, quest_title: str, tier: int, xp_penalty: int, action: str) -> None:
        database_manager.execute(
            """
            INSERT INTO enforcement_log (enforcement_date, missed_quest_title, tier, xp_penalty, action_taken, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (date.today().isoformat(), quest_title, tier, xp_penalty, action, datetime.now().isoformat())
        )

    # ── ENFORCEMENT TIERS ─────────────────────────────────────────────────────

    def _tier1_soft(self, quest: dict, miss_streak: int) -> None:
        """Tier 1: XP penalty + voice callout. Consequence is felt but recoverable."""
        penalty = self._apply_xp_penalty(quest)
        msg = (
            f"Sir, quest '{quest['description'][:60]}' was not completed today. "
            f"{penalty} XP has been deducted. Consecutive miss day count: {miss_streak}. "
            f"A recovery contract has been issued for tomorrow. Do not let it happen again."
        )
        print(f"[Enforcer][TIER 1] {msg}")
        try:
            speak_text(msg)
        except Exception:
            pass
        self._log_enforcement(quest["title"], 1, penalty, "XP penalty + voice callout")

    def _tier2_hard(self, quest: dict, miss_streak: int) -> None:
        """Tier 2: Tier 1 + activate Focus Guard for 2 hours."""
        penalty = self._apply_xp_penalty(quest)
        msg = (
            f"Two consecutive failure days detected, Sir. Quest '{quest['description'][:50]}' missed again. "
            f"{penalty} XP deducted. Focus Guard is now activating — distractions will be blocked "
            f"for the next two hours. Discipline must be rebuilt, not negotiated."
        )
        print(f"[Enforcer][TIER 2] {msg}")
        try:
            speak_text(msg)
        except Exception:
            pass
        # Activate Focus Guard
        try:
            from automation.focus_guard import FocusGuard
            guard = FocusGuard()
            guard.activate(duration_minutes=120)
            print("[Enforcer] Focus Guard activated for 120 minutes.")
        except Exception as exc:
            print(f"[Enforcer] Focus Guard activation failed: {exc}")
        self._log_enforcement(quest["title"], 2, penalty, "XP penalty + focus guard activated")

    def _tier3_hostile(self, quest: dict, miss_streak: int) -> None:
        """
        Tier 3: Full Penalty Zone.
        XP penalty + Focus Guard + mandatory accountability statement required before
        the system allows normal operation tomorrow.
        """
        penalty = self._apply_xp_penalty(quest)
        msg = (
            f"CRITICAL: {miss_streak} consecutive days of failure. Penalty Zone activated. "
            f"Quest '{quest['description'][:50]}' missed for the third time. "
            f"{penalty} XP stripped. Tomorrow's system launch will be locked until a written "
            f"accountability statement is submitted. There are no shortcuts, Sir."
        )
        print(f"[Enforcer][TIER 3 — PENALTY ZONE] {msg}")
        try:
            speak_text(msg)
        except Exception:
            pass
        # Flag accountability statement required
        self._set_accountability_due(True)
        # Activate Focus Guard
        try:
            from automation.focus_guard import FocusGuard
            guard = FocusGuard()
            guard.activate(duration_minutes=120)
        except Exception as exc:
            print(f"[Enforcer] Focus Guard activation failed: {exc}")
        self._log_enforcement(quest["title"], 3, penalty, "XP penalty + penalty zone + accountability required")

    # ── ACCOUNTABILITY GATE ───────────────────────────────────────────────────

    def check_accountability_gate(self) -> bool:
        """
        Called at system startup. If an accountability statement is due (from a Tier 3
        enforcement), block normal operation and collect the statement.

        Returns True if the gate is clear (normal boot allowed).
        Returns False if the gate is blocked and was NOT resolved.
        """
        if not self.accountability_is_due():
            return True

        print()
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║            ⚠  PENALTY ZONE — SYSTEM LOCKED  ⚠            ║")
        print("╠═══════════════════════════════════════════════════════════╣")
        print("║  You failed critical quests for 3+ consecutive days.      ║")
        print("║  Before the system unlocks, you must submit an            ║")
        print("║  accountability statement (minimum 150 characters).       ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print()

        try:
            speak_text(
                "Penalty Zone is active, Sir. Submit your accountability statement to unlock the system."
            )
        except Exception:
            pass

        print("What failed? Why? What will be different tomorrow?")
        print("(Type your statement below, press Enter twice when done)\n")

        lines = []
        while True:
            try:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                print("\n[Enforcer] Input interrupted. System remains locked.")
                return False

        statement = "\n".join(lines).strip()
        if len(statement) < 150:
            print(f"\n[Enforcer] Statement too short ({len(statement)} chars). Minimum 150 required.")
            print("System remains locked. Try again tomorrow.")
            return False

        # Save accountability statement to shadow journal
        database_manager.execute(
            "INSERT INTO shadow_journal (content, category, created_at) VALUES (?, ?, ?)",
            (statement, "accountability", datetime.now().isoformat())
        )
        self._set_accountability_due(False)
        self._reset_miss_streak()
        print("\n[Enforcer] Statement accepted. Penalty Zone lifted. Penalty streak reset.")
        print("Do not waste this chance.\n")
        try:
            speak_text("Accountability accepted. Penalty Zone lifted. The system is online. Make it count.")
        except Exception:
            pass
        return True

    # ── MAIN ENFORCEMENT RUN ──────────────────────────────────────────────────

    def run(self) -> dict:
        """
        Execute the full midnight enforcement sequence.
        Call this at 23:45 via Task Scheduler or the daemon scheduler.
        """
        print()
        print("╔══════════════════════════════════════════╗")
        print("║   APEX GHOST — MIDNIGHT ENFORCER ACTIVE  ║")
        print(f"║   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║")
        print("╚══════════════════════════════════════════╝")

        pending = self._get_todays_pending_critical_quests()
        completed_count = self._get_todays_completed_critical_quests()

        if not pending:
            # Hunter cleared everything — reward the streak
            self._reset_miss_streak()
            msg = f"All critical quests completed today, Sir. Streak maintained. Execution confirmed."
            print(f"\n[Enforcer] CLEAN DAY — {completed_count} critical quest(s) completed.")
            try:
                speak_text(msg)
            except Exception:
                pass
            return {"status": "clean", "missed": 0, "completed": completed_count}

        # Hunter failed — increment miss streak and enforce
        miss_streak = self._increment_miss_streak()
        missed_titles = [q["description"][:60] for q in pending]

        print(f"\n[Enforcer] FAILURE DAY — {len(pending)} critical quest(s) missed.")
        print(f"[Enforcer] Consecutive miss days: {miss_streak}")

        for quest in pending:
            if miss_streak >= self.TIER_3_THRESHOLD:
                self._tier3_hostile(quest, miss_streak)
            elif miss_streak >= self.TIER_2_THRESHOLD:
                self._tier2_hard(quest, miss_streak)
            else:
                self._tier1_soft(quest, miss_streak)

        # Always spawn a recovery quest on any failure
        self._spawn_recovery_quest(missed_titles)

        return {
            "status": "enforced",
            "missed": len(pending),
            "completed": completed_count,
            "tier": min(miss_streak, 3),
            "miss_streak": miss_streak,
        }


# ── ENTRY POINTS ──────────────────────────────────────────────────────────────

def run_midnight_enforcement() -> dict:
    """Called by Task Scheduler at 23:45 every night."""
    enforcer = MidnightEnforcer()
    return enforcer.run()


def check_accountability_gate() -> bool:
    """Called at system startup (main.py / daily_orchestrator) before anything else runs."""
    enforcer = MidnightEnforcer()
    return enforcer.check_accountability_gate()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Apex Ghost Midnight Enforcer")
    parser.add_argument("--gate", action="store_true",
                        help="Run the accountability gate check (call at startup)")
    args = parser.parse_args()

    if args.gate:
        cleared = check_accountability_gate()
        sys.exit(0 if cleared else 1)
    else:
        result = run_midnight_enforcement()
        print(f"\nEnforcement result: {result}")
