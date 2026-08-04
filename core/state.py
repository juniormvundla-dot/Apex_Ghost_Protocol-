from __future__ import annotations

# This file stores simple state information for Apex Ghost.
# State means small bits of information about what the system has already done.
# For example:
# - Did awakening already run today?
# - What mode is the system currently in?
# - When was the last action performed?

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class SystemState:
    """
    A lightweight container for system status.

    This is not a database.
    It is only a simple in-memory state object that can be expanded later.
    """

    # The date when awakening last ran successfully
    last_awakening_date: date | None = None

    # The date and time when the last major action happened
    last_action_time: datetime | None = None

    # The current mode of the system
    # Examples: "idle", "awakening", "private_mode", "deep_work"
    current_mode: str = "idle"

    # Whether the system is currently active
    is_active: bool = False

    # Optional notes for debugging or future extensions
    notes: dict[str, str] = field(default_factory=dict)

    def mark_awakening_complete(self) -> None:
        """
        Record that the awakening protocol completed successfully.
        """
        self.last_awakening_date = date.today()
        self.last_action_time = datetime.now()
        self.current_mode = "awake"
        self.is_active = True

    def awakening_ran_today(self) -> bool:
        """
        Return True if awakening already happened today.
        """
        return self.last_awakening_date == date.today()

    def set_mode(self, mode: str) -> None:
        """
        Update the current mode of the system.
        """
        self.current_mode = mode
        self.last_action_time = datetime.now()