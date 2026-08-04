from __future__ import annotations

# This is a small manual test for the storage layer.
# It creates a sample quest, saves it, and loads it back from the database.

from datetime import date

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from quests.models import Quest, QuestLevel
from storage.db import database_manager
from storage.repositories import quest_repository


def main() -> None:
    # Make sure the database and tables are ready before saving anything.
    database_manager.ensure_ready()

    # Create a sample quest for testing.
    quest = Quest(
        title="Test Daily Quest",
        description="A test quest to verify database storage.",
        level=QuestLevel.DAILY,
        target_date=date.today(),
        notes="Created during storage test.",
    )

    # Save the quest into the SQLite database.
    quest_repository.save_quest(quest)
    print("Quest saved successfully.")

    # Load all quests from the database and print the latest one.
    quests = quest_repository.get_all_quests()
    print(f"Total quests loaded: {len(quests)}")

    if quests:
        latest = quests[0]
        print("\nLatest quest:")
        print(f"Title: {latest.title}")
        print(f"Description: {latest.description}")
        print(f"Level: {latest.level.value}")
        print(f"Status: {latest.status.value}")


if __name__ == "__main__":
    main()