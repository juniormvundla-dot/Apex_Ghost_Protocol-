from __future__ import annotations

# Main entry point for Apex Ghost.

import argparse
import sys

from core.logging_setup import setup_logging
from core.paths import paths
from storage.db import database_manager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apex Ghost discipline system")
    parser.add_argument(
        "command",
        nargs="?",
        default="menu",
        choices=["menu", "daily", "scheduler"],
        help="Run the CLI menu, daily protocol, or awakening scheduler",
    )
    return parser


def main() -> None:
    logger = setup_logging()

    try:
        paths.ensure_exists()
        database_manager.ensure_ready()
        logger.info("Project paths and database verified successfully.")

        parser = build_parser()
        args = parser.parse_args()

        if args.command == "daily":
            from core.daily_orchestrator import run_daily_protocol

            logger.info("Starting daily protocol...")
            run_daily_protocol()
            return

        if args.command == "scheduler":
            from automation.scheduler import start_scheduler

            logger.info("Starting awakening scheduler...")
            start_scheduler()
            return

        from ui.cli import main as run_cli_menu

        logger.info("Starting Apex Ghost CLI menu...")
        run_cli_menu()

    except KeyboardInterrupt:
        logger.info("Apex Ghost stopped by user.")
        sys.exit(0)

    except Exception as exc:
        logger.exception(f"Fatal error in main(): {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
