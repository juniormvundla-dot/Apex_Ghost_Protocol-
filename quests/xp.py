from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from storage.db import database_manager


@dataclass
class XPState:
    total_xp: int = 0
    rank: str = "E"
    streak: int = 0
    last_active_date: date | None = None
    missed_wake_ups: int = 0


class XPSystem:
    """
    Handles XP accumulation, rank progression, and streak tracking.
    """

    def __init__(self) -> None:
        self.state = XPState()
        self._load()

    def add_xp(self, amount: int) -> None:
        self.state.total_xp += max(amount, 0)
        self._update_rank()
        self._save()

    def apply_penalty(self, amount: int) -> None:
        self.state.total_xp = max(0, self.state.total_xp - max(amount, 0))
        self._update_rank()
        self._save()

    def mark_active_day(self, active_date: date | None = None) -> None:
        active_date = active_date or date.today()

        if self.state.last_active_date == active_date:
            return

        if self.state.last_active_date is not None:
            day_gap = (active_date - self.state.last_active_date).days
            if day_gap == 1:
                self.state.streak += 1
            elif day_gap > 1:
                self.state.streak = 1
        else:
            self.state.streak = 1

        self.state.last_active_date = active_date
        self._update_rank()
        self._save()

    def record_missed_wake_up(self) -> None:
        self.state.missed_wake_ups += 1
        self._save()

    def _update_rank(self) -> None:
        xp = self.state.total_xp
        streak = self.state.streak

        # Logarithmic rank thresholds — aligned to 90-day discipline arcs.
        # Rank S requires 12+ months of elite, consistent execution.
        # Streak bonuses allow fast early ranks but cannot skip tiers.
        if xp >= 35_000 or (xp >= 20_000 and streak >= 90):
            self.state.rank = "S"
        elif xp >= 15_000 or (xp >= 8_000 and streak >= 60):
            self.state.rank = "A"
        elif xp >= 6_000 or (xp >= 3_000 and streak >= 30):
            self.state.rank = "B"
        elif xp >= 2_000 or (xp >= 800 and streak >= 14):
            self.state.rank = "C"
        elif xp >= 500 or (xp >= 150 and streak >= 5):
            self.state.rank = "D"
        else:
            self.state.rank = "E"

    # XP thresholds per rank — used for progress bar calculation
    RANK_THRESHOLDS: dict[str, tuple[int, int]] = {
        "E": (0,       500),
        "D": (500,     2_000),
        "C": (2_000,   6_000),
        "B": (6_000,   15_000),
        "A": (15_000,  35_000),
        "S": (35_000,  35_000),  # Max rank — no ceiling
    }

    def get_summary(self) -> dict[str, int | str]:
        return {
            "total_xp": self.state.total_xp,
            "rank": self.state.rank,
            "streak": self.state.streak,
            "missed_wake_ups": self.state.missed_wake_ups,
        }

    def _load(self) -> None:
        database_manager.ensure_ready()
        row = database_manager.fetch_one(
            """
            SELECT total_xp, rank, streak, last_active_date, missed_wake_ups
            FROM player_state
            WHERE id = 1
            """
        )
        if row is None:
            self._save()
            return

        self.state = XPState(
            total_xp=row["total_xp"],
            rank=row["rank"],
            streak=row["streak"],
            last_active_date=date.fromisoformat(row["last_active_date"])
            if row["last_active_date"]
            else None,
            missed_wake_ups=row["missed_wake_ups"],
        )

    def _save(self) -> None:
        database_manager.execute(
            """
            INSERT INTO player_state (id, total_xp, rank, streak, last_active_date, missed_wake_ups)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                total_xp = excluded.total_xp,
                rank = excluded.rank,
                streak = excluded.streak,
                last_active_date = excluded.last_active_date,
                missed_wake_ups = excluded.missed_wake_ups
            """,
            (
                self.state.total_xp,
                self.state.rank,
                self.state.streak,
                self.state.last_active_date.isoformat()
                if self.state.last_active_date
                else None,
                self.state.missed_wake_ups,
            ),
        )


xp_system = XPSystem()
