from __future__ import annotations

# This file contains repository classes for working with stored data.
# A repository is a small layer between your Python objects and the database.
# It keeps database code separate from business logic.

from datetime import date, datetime
from typing import Optional

from quests.models import Quest, QuestCategory, QuestLevel, QuestStatus
from quests.progress import QuestProgressRecord
from quests.penalties import PenaltyRecord
from storage.db import database_manager


class QuestRepository:
    """
    Handles saving and loading quests from the database.
    """

    def _row_to_quest(self, row) -> Quest:
        return Quest(
            title=row["title"],
            description=row["description"],
            level=QuestLevel(row["level"]),
            target_date=datetime.fromisoformat(row["target_date"]).date()
            if row["target_date"]
            else None,
            completed_at=datetime.fromisoformat(row["completed_at"])
            if row["completed_at"]
            else None,
            status=QuestStatus(row["status"]),
            notes=row["notes"] or "",
            category=QuestCategory(row["category"]) if row["category"] else QuestCategory.CORE,
            difficulty=row["difficulty"] if row["difficulty"] is not None else 2,
            xp_reward=row["xp_reward"] if row["xp_reward"] is not None else 100,
            penalty_xp=row["penalty_xp"] if row["penalty_xp"] is not None else 50,
            evidence_required=bool(row["evidence_required"]) if "evidence_required" in row.keys() else False,
            evidence_submitted=row["evidence_submitted"] if "evidence_submitted" in row.keys() else "",
        )

    def save_quest(self, quest: Quest) -> None:
        """
        Insert or update a quest in the database.
        """
        database_manager.execute(
            """
            INSERT INTO quests (
                title, description, level, status, target_date, completed_at, notes,
                category, difficulty, xp_reward, penalty_xp, evidence_required, evidence_submitted
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                description = excluded.description,
                level = excluded.level,
                status = excluded.status,
                target_date = excluded.target_date,
                completed_at = excluded.completed_at,
                notes = excluded.notes,
                category = excluded.category,
                difficulty = excluded.difficulty,
                xp_reward = excluded.xp_reward,
                penalty_xp = excluded.penalty_xp,
                evidence_required = excluded.evidence_required,
                evidence_submitted = excluded.evidence_submitted
            """,
            (
                quest.title,
                quest.description,
                quest.level.value,
                quest.status.value,
                quest.target_date.isoformat() if quest.target_date else None,
                quest.completed_at.isoformat() if quest.completed_at else None,
                quest.notes,
                quest.category.value,
                quest.difficulty,
                quest.xp_reward,
                quest.penalty_xp,
                int(quest.evidence_required),
                quest.evidence_submitted,
            ),
        )

    def get_all_quests(self) -> list[Quest]:
        """
        Load all quests from the database.
        """
        rows = database_manager.fetch_all(
            """
            SELECT title, description, level, status, target_date, completed_at, notes,
                   category, difficulty, xp_reward, penalty_xp, evidence_required, evidence_submitted
            FROM quests
            ORDER BY id DESC
            """
        )

        return [self._row_to_quest(row) for row in rows]

    def find_by_status(self, status: QuestStatus) -> list[Quest]:
        """
        Load quests that match a specific status.
        """
        rows = database_manager.fetch_all(
            """
            SELECT title, description, level, status, target_date, completed_at, notes,
                   category, difficulty, xp_reward, penalty_xp, evidence_required, evidence_submitted
            FROM quests
            WHERE status = ?
            ORDER BY id DESC
            """,
            (status.value,),
        )

        return [self._row_to_quest(row) for row in rows]

    def find_daily_by_date(self, target_date: date) -> list[Quest]:
        """
        Load daily quests scheduled for a specific date.
        """
        rows = database_manager.fetch_all(
            """
            SELECT title, description, level, status, target_date, completed_at, notes,
                   category, difficulty, xp_reward, penalty_xp, evidence_required, evidence_submitted
            FROM quests
            WHERE level = ? AND target_date = ?
            ORDER BY id ASC
            """,
            (QuestLevel.DAILY.value, target_date.isoformat()),
        )

        return [self._row_to_quest(row) for row in rows]


class ProgressRepository:
    """
    Handles saving quest progress records.
    """

    def save_progress(self, record: QuestProgressRecord) -> None:
        """
        Store a progress record in the database.
        """
        database_manager.execute(
            """
            INSERT INTO quest_progress (quest_title, status, timestamp, notes)
            VALUES (?, ?, ?, ?)
            """,
            (
                record.quest_title,
                record.status.value,
                record.timestamp.isoformat(),
                record.notes,
            ),
        )

    def get_recent_progress(self, limit: int = 10) -> list[QuestProgressRecord]:
        """
        Load the most recent progress records.
        """
        rows = database_manager.fetch_all(
            """
            SELECT quest_title, status, timestamp, notes
            FROM quest_progress
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        records: list[QuestProgressRecord] = []
        for row in rows:
            records.append(
                QuestProgressRecord(
                    quest_title=row["quest_title"],
                    status=QuestStatus(row["status"]),
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    notes=row["notes"] or "",
                )
            )

        return records


class PenaltyRepository:
    """
    Handles saving penalty records.
    """

    def save_penalty(self, record: PenaltyRecord) -> None:
        """
        Store a penalty record in the database.
        """
        database_manager.execute(
            """
            INSERT INTO penalties (quest_title, reason, corrective_action, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                record.quest_title,
                record.reason,
                record.corrective_action,
                record.timestamp.isoformat(),
            ),
        )

    def get_recent_penalties(self, limit: int = 10) -> list[PenaltyRecord]:
        """
        Load the most recent penalty records.
        """
        rows = database_manager.fetch_all(
            """
            SELECT quest_title, reason, corrective_action, timestamp
            FROM penalties
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        records: list[PenaltyRecord] = []
        for row in rows:
            records.append(
                PenaltyRecord(
                    quest_title=row["quest_title"],
                    reason=row["reason"],
                    corrective_action=row["corrective_action"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                )
            )

        return records


# Reusable repository instances.
quest_repository = QuestRepository()
progress_repository = ProgressRepository()
penalty_repository = PenaltyRepository()