from __future__ import annotations

import json
from datetime import datetime, timedelta
from storage.db import database_manager
from quests.xp import xp_system

class RaidService:
    """
    Raid Service managing Solo Dungeons, Boss Raids, and Checkpoints.
    """

    def get_active_raid(self) -> dict | None:
        database_manager.ensure_ready()
        raid = database_manager.fetch_one(
            "SELECT * FROM raids WHERE status = 'ACTIVE' ORDER BY id DESC LIMIT 1"
        )
        if not raid:
            return None

        raid_dict = dict(raid)
        checkpoints = database_manager.fetch_all(
            "SELECT * FROM raid_checkpoints WHERE raid_id = ? ORDER BY id ASC",
            (raid_dict["id"],)
        )
        raid_dict["checkpoints"] = [dict(c) for c in checkpoints]
        
        # Calculate progress
        total = len(raid_dict["checkpoints"])
        completed = sum(1 for c in raid_dict["checkpoints"] if c["status"] == "COMPLETED")
        raid_dict["progress_pct"] = int((completed / total) * 100) if total > 0 else 0
        return raid_dict

    def start_solo_dungeon(self, raid_name: str = "THE IRON GAUNTLET", domain: str = "WARRIOR", difficulty: str = "VETERAN") -> dict:
        database_manager.ensure_ready()
        
        # Check if active raid already exists
        active = self.get_active_raid()
        if active:
            return active

        now = datetime.now()
        deadline = now + timedelta(hours=24)

        cursor = database_manager.execute(
            """
            INSERT INTO raids (raid_name, raid_type, difficulty, domain, status, party_hp_current, party_hp_max, started_at, deadline_at)
            VALUES (?, 'SOLO', ?, ?, 'ACTIVE', 1000, 1000, ?, ?)
            """,
            (raid_name, difficulty, domain, now.isoformat(), deadline.isoformat())
        )
        raid_id = cursor.lastrowid

        # Insert 4 default checkpoints across the 24-hour dungeon window
        checkpoints = [
            ("Phase 1: Awakening & Core Protocol", (now + timedelta(hours=3)).strftime("%H:%M")),
            ("Phase 2: Deep Work Block (2h+)", (now + timedelta(hours=8)).strftime("%H:%M")),
            ("Phase 3: Domain Execution & Trial", (now + timedelta(hours=14)).strftime("%H:%M")),
            ("Phase 4: Midnight Recon & Journal", (now + timedelta(hours=20)).strftime("%H:%M"))
        ]

        for title, target_time in checkpoints:
            database_manager.execute(
                """
                INSERT INTO raid_checkpoints (raid_id, title, target_time, status)
                VALUES (?, ?, ?, 'PENDING')
                """,
                (raid_id, title, target_time)
            )

        return self.get_active_raid()

    def complete_checkpoint(self, checkpoint_id: int, evidence: str = "Verified") -> dict:
        database_manager.ensure_ready()
        database_manager.execute(
            """
            UPDATE raid_checkpoints 
            SET status = 'COMPLETED', evidence_submitted = ?, completed_at = datetime('now')
            WHERE id = ?
            """,
            (evidence, checkpoint_id)
        )

        # Check if all checkpoints are now complete
        checkpoint = database_manager.fetch_one(
            "SELECT raid_id FROM raid_checkpoints WHERE id = ?",
            (checkpoint_id,)
        )
        if checkpoint:
            raid_id = checkpoint["raid_id"]
            remaining = database_manager.fetch_one(
                "SELECT COUNT(*) as count FROM raid_checkpoints WHERE raid_id = ? AND status != 'COMPLETED'",
                (raid_id,)
            )
            if remaining and remaining["count"] == 0:
                # Dungeon cleared!
                database_manager.execute(
                    "UPDATE raids SET status = 'COMPLETED', completed_at = datetime('now') WHERE id = ?",
                    (raid_id,)
                )
                raid = database_manager.fetch_one("SELECT domain FROM raids WHERE id = ?", (raid_id,))
                domain = raid["domain"] if raid else "WARRIOR"
                
                # Award victory XP
                xp_system.add_xp(600, stream=domain)

        return self.get_active_raid() or {}

    def damage_raid(self, raid_id: int, hp_loss: int = 150) -> dict:
        database_manager.ensure_ready()
        raid = database_manager.fetch_one("SELECT party_hp_current FROM raids WHERE id = ?", (raid_id,))
        if not raid:
            return {}

        new_hp = max(0, raid["party_hp_current"] - hp_loss)
        status = "FAILED" if new_hp == 0 else "ACTIVE"

        database_manager.execute(
            "UPDATE raids SET party_hp_current = ?, status = ? WHERE id = ?",
            (new_hp, status, raid_id)
        )
        return self.get_active_raid() or {}

raid_service = RaidService()
