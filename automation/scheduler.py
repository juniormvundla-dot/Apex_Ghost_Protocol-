from __future__ import annotations

# This file controls WHEN the awakening protocol should run.
# It does not play videos itself.
# Instead, it checks the clock and launches the awakening engine at the right time.

from datetime import datetime
import time

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from automation.awakening import MorningAwakeningProtocol
from core.config import config


class AwakeningScheduler:
    """
    Scheduler for the Morning Awakening Protocol.

    Responsibilities:
    - check the current time
    - trigger awakening at or after the target hour
    - avoid running multiple times in one day
    """

    def __init__(
        self,
        target_hour: int | None = None,
        target_minute: int | None = None,
    ) -> None:
        self.target_hour = target_hour if target_hour is not None else config.awakening.target_hour
        self.target_minute = (
            target_minute if target_minute is not None else config.awakening.target_minute
        )

        # Create the awakening protocol once and reuse it
        self.protocol = MorningAwakeningProtocol()

    def should_trigger_now(self) -> bool:
        """
        Return True if the current time is at or after the scheduled wake-up time.
        """
        now = datetime.now()
        return (
            now.hour > self.target_hour
            or (now.hour == self.target_hour and now.minute >= self.target_minute)
        )

    def run_once_if_due(self) -> None:
        """
        Check whether the awakening should run right now.

        If the time is correct and it has not already run today,
        start the awakening protocol.
        """
        if not self.should_trigger_now():
            return

        # The awakening engine already prevents duplicate runs on the same day.
        self.protocol.run()

    def run_forever(self, poll_seconds: int = 60) -> None:
        """
        Keep checking the clock in the background.

        poll_seconds controls how often the scheduler checks the time.
        A value of 60 means it checks once per minute.
        """
        print(
            f"Awakening scheduler started. "
            f"Waiting for {self.target_hour:02d}:{self.target_minute:02d}..."
        )

        while True:
            try:
                self.run_once_if_due()
            except Exception as exc:
                # If something goes wrong, print the error and keep the scheduler alive.
                print(f"Scheduler error: {exc}")

            # Sleep before checking again
            time.sleep(poll_seconds)


def start_scheduler() -> None:
    """
    Convenience function to start the scheduler from another file.
    """
    scheduler = AwakeningScheduler()
    scheduler.run_forever()


if __name__ == "__main__":
    start_scheduler()
