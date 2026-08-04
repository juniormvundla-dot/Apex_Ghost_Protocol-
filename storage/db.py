from __future__ import annotations

# This file manages the SQLite database connection for Apex Ghost.
# SQLite is a lightweight local database that stores data in a single file.
# It is a good choice for quest tracking, progress logs, penalties, and state.

import sqlite3
import threading

from core.paths import paths


class DatabaseManager:
    """
    Manages the SQLite database connection and initialization.

    Responsibilities:
    - create the database file if needed
    - open and close connections safely
    - create tables for future storage use
    """

    def __init__(self, db_filename: str = "apex_ghost.db") -> None:
        self.db_path = paths.storage_dir / db_filename
        self.connection: sqlite3.Connection | None = None
        self.lock = threading.Lock()

        # Make sure the storage directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """
        Open a database connection and keep it available.
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

        return self.connection

    def close(self) -> None:
        """
        Close the database connection if it is open.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Run a SQL statement and commit the change.
        """
        with self.lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor

    def fetch_all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        Run a SELECT query and return all rows.
        """
        with self.lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()

    def fetch_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        """
        Run a SELECT query and return one row.
        """
        with self.lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()

    def initialize_tables(self) -> None:
        """
        Create the core tables used by the project.
        """
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                level TEXT NOT NULL,
                status TEXT NOT NULL,
                target_date TEXT,
                completed_at TEXT,
                notes TEXT,
                evidence_required INTEGER DEFAULT 0,
                evidence_submitted TEXT
            )
            """
        )

        try:
            self.execute("ALTER TABLE quests ADD COLUMN evidence_required INTEGER DEFAULT 0")
            self.execute("ALTER TABLE quests ADD COLUMN evidence_submitted TEXT")
        except Exception:
            pass # Columns likely already exist

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS quest_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_title TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                notes TEXT
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS penalties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_title TEXT NOT NULL,
                reason TEXT NOT NULL,
                corrective_action TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS player_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_xp INTEGER NOT NULL DEFAULT 0,
                rank TEXT NOT NULL DEFAULT 'E',
                streak INTEGER NOT NULL DEFAULT 0,
                last_active_date TEXT,
                missed_wake_ups INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                completed INTEGER DEFAULT 0
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS shadow_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS player_attributes (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                strength INTEGER NOT NULL DEFAULT 10,
                intelligence INTEGER NOT NULL DEFAULT 10,
                agility INTEGER NOT NULL DEFAULT 10,
                discipline INTEGER NOT NULL DEFAULT 10,
                last_decay_check TEXT
            )
            """
        )
        self.execute("INSERT OR IGNORE INTO player_attributes (id, strength, intelligence, agility, discipline) VALUES (1, 10, 10, 10, 10)")

        self._migrate_quest_columns()

    def _migrate_quest_columns(self) -> None:
        """
        Add gamification columns to quests when upgrading an older database.
        """
        rows = self.fetch_all("PRAGMA table_info(quests)")
        existing = {row["name"] for row in rows}

        migrations = {
            "category": "ALTER TABLE quests ADD COLUMN category TEXT NOT NULL DEFAULT 'core'",
            "difficulty": "ALTER TABLE quests ADD COLUMN difficulty INTEGER NOT NULL DEFAULT 2",
            "xp_reward": "ALTER TABLE quests ADD COLUMN xp_reward INTEGER NOT NULL DEFAULT 100",
            "penalty_xp": "ALTER TABLE quests ADD COLUMN penalty_xp INTEGER NOT NULL DEFAULT 50",
        }

        for column, sql in migrations.items():
            if column not in existing:
                self.execute(sql)

    def ensure_ready(self) -> None:
        """
        Make sure the database exists and tables are ready.
        """
        self.connect()
        self.initialize_tables()


# Reusable instance for other modules to import.
database_manager = DatabaseManager()