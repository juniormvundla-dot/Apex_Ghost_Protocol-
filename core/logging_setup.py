from __future__ import annotations

# This file configures logging for the entire Apex Ghost system.
# Logging is useful because it keeps a history of what the program did,
# which helps with debugging and future improvements.

import logging
from pathlib import Path

from core.paths import paths


def setup_logging(log_file_name: str = "apex_ghost.log") -> logging.Logger:
    """
    Create and return a configured logger.

    This logger writes messages to:
    - the console, so you can see what is happening live
    - a log file, so you can review events later
    """
    log_dir = paths.project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file_path = log_dir / log_file_name

    logger = logging.getLogger("ApexGhostSystem")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logging is called more than once
    if logger.handlers:
        return logger

    # Format used for both console and file output
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler: shows logs in the terminal or IDE console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler: writes logs to a file in /logs
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logging system initialized.")
    logger.info(f"Log file: {log_file_path}")

    return logger