from __future__ import annotations

# This is a simple end-to-end test for the quest system.
# It creates a quest, starts it, completes it, and prints summaries.

from datetime import date

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from quests.service import quest_service


def main() -> None:
    print("Starting quest flow test...")

    # Create a daily quest
    quest = quest_service.create_daily_quest(
        title="Test Daily Quest",
        description="A test quest to verify the quest service flow.",
        target_date=date.today(),
        notes="Created during quest flow test.",
    )
    print(f"Created quest: {quest.title}")

    # Start the quest
    quest_service.start_quest(quest)
    print(f"Started quest: {quest.title}")

    # Complete the quest
    quest_service.complete_quest(quest, notes="Quest completed during test.")
    print(f"Completed quest: {quest.title}")

    # Print summaries
    quest_service.print_progress_summary()

    print("\nQuest flow test complete.")


if __name__ == "__main__":
    main()