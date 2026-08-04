from __future__ import annotations

# This file centralizes all important project paths.
# The goal is to avoid hardcoding folder locations in multiple files.

from pathlib import Path


class ProjectPaths:
    """
    Central place for resolving important directories in the project.

    Use this class whenever another module needs to find:
    - the project root
    - the assets folder
    - the core folder
    - the automation folder
    """

    def __init__(self) -> None:
        # Resolve the project root by moving one level up from /core
        self.project_root: Path = Path(__file__).resolve().parent.parent

        # Common project folders
        self.assets_dir: Path = self.project_root / "assets"
        self.core_dir: Path = self.project_root / "core"
        self.automation_dir: Path = self.project_root / "automation"
        self.voice_dir: Path = self.project_root / "voice"
        self.scrapers_dir: Path = self.project_root / "scrapers"
        self.storage_dir: Path = self.project_root / "storage"
        self.ui_dir: Path = self.project_root / "ui"

    def ensure_exists(self) -> None:
        """
        Check that the most important folders exist.

        This is useful during startup so the program can fail early
        if the project structure is broken.
        """
        required_dirs = [
            self.project_root,
            self.assets_dir,
            self.core_dir,
            self.automation_dir,
        ]

        for folder in required_dirs:
            if not folder.exists():
                raise FileNotFoundError(f"Required folder not found: {folder}")

    def asset_path(self, filename: str) -> Path:
        """
        Return the full path to a file inside the assets folder.
        """
        return self.assets_dir / filename


# Create one reusable instance so other files can import it easily.
paths = ProjectPaths()
