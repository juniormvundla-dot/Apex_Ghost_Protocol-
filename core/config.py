from __future__ import annotations

# Central configuration for Apex Ghost.
# Values load from core/apex_ghost_config.json when present,
# otherwise sensible defaults are used and written on first save.

import json
from dataclasses import asdict, dataclass, field

from core.paths import paths


@dataclass
class AwakeningConfig:
    target_hour: int = 5
    target_minute: int = 0
    vlc_path: str = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    run_on_daily_start: bool = True
    skip_if_already_ran: bool = True


@dataclass
class PrivateModeConfig:
    launch_intellij: bool = True
    launch_browser: bool = True
    play_voice_greeting: bool = True
    min_deep_work_minutes: int = 45
    voice_profile: str = "jinwoo"
    use_elevenlabs: bool = False
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "ODq5zmih8GrV2aMhZaec"
    browser_name: str = "brave"
    use_gemini: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    enable_process_guard: bool = True
    blocked_processes: list[str] = field(
        default_factory=lambda: ["Discord.exe", "Steam.exe", "Spotify.exe", "epicgameslauncher.exe"]
    )
    enable_hosts_block: bool = False
    blocked_domains: list[str] = field(
        default_factory=lambda: ["youtube.com", "twitter.com", "reddit.com", "instagram.com", "facebook.com"]
    )
    intellij_path: str = r"C:\Users\tmvundla\Downloads\idea-2026.1.win\bin\idea64.exe"
    browser_tabs: list[str] = field(
        default_factory=lambda: [
            "https://www.google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://dev.to",
            "https://news.ycombinator.com",
        ]
    )


@dataclass
class DailyFlowConfig:
    offer_private_mode: bool = True
    offer_intelligence_brief: bool = False
    interactive_quest_completion: bool = True


@dataclass
class CloudBackupConfig:
    enable_aws_sync: bool = False
    aws_bucket_name: str = "apex-ghost-backup-bucket"
    aws_region: str = "af-south-1"


@dataclass
class ApexGhostConfig:
    awakening: AwakeningConfig = field(default_factory=AwakeningConfig)
    private_mode: PrivateModeConfig = field(default_factory=PrivateModeConfig)
    daily_flow: DailyFlowConfig = field(default_factory=DailyFlowConfig)
    cloud_backup: CloudBackupConfig = field(default_factory=CloudBackupConfig)

    @property
    def config_path(self):
        return paths.core_dir / "apex_ghost_config.json"

    @classmethod
    def load(cls) -> ApexGhostConfig:
        path = paths.core_dir / "apex_ghost_config.json"
        if not path.exists():
            config = cls()
            config.save()
            return config

        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            awakening=AwakeningConfig(**data.get("awakening", {})),
            private_mode=PrivateModeConfig(**data.get("private_mode", {})),
            daily_flow=DailyFlowConfig(**data.get("daily_flow", {})),
            cloud_backup=CloudBackupConfig(**data.get("cloud_backup", {})),
        )

    def save(self) -> None:
        payload = {
            "awakening": asdict(self.awakening),
            "private_mode": asdict(self.private_mode),
            "daily_flow": asdict(self.daily_flow),
            "cloud_backup": asdict(self.cloud_backup),
        }
        self.config_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )


config = ApexGhostConfig.load()
