from __future__ import annotations

# Command-line menu for Apex Ghost.

from automation.awakening import run_awakening_protocol
from automation.private_mode import activate_private_mode
from automation.scheduler import start_scheduler
from core.daily_orchestrator import run_daily_protocol
from quests.test_quest_flow import main as run_quest_flow_test
from storage.test_storage import main as run_storage_test


def print_menu() -> None:
    print("\n=================================")
    print("      APEX GHOST COMMAND MENU")
    print("=================================")
    print("1. Start My Day (Daily Protocol)")
    print("2. Set Up Yearly Goals")
    print("3. View Execution Plan")
    print("4. Begin Morning Awakening")
    print("5. Enter Private Mode")
    print("6. Run Intelligence Brief")
    print("7. Start Awakening Scheduler")
    print("8. Start Web HUD Dashboard")
    print("9. Developer Tools")
    print("10. Force Cloud Sync")
    print("11. Treasury & Arbitrage Protocol")
    print("12. Exit")
    print()


def print_dev_menu() -> None:
    print("\n--- Developer Tools ---")
    print("1. Run Quest Flow Test")
    print("2. Run Storage Test")
    print("3. Back")


def handle_dev_choice(choice: str) -> bool:
    if choice == "1":
        print("\n>> Running Quest Flow Test...")
        run_quest_flow_test()
        return True

    if choice == "2":
        print("\n>> Running Storage Test...")
        run_storage_test()
        return True

    if choice == "3":
        return False

    print("Invalid choice.")
    return True


def handle_choice(choice: str) -> bool:
    if choice == "1":
        print("\n>> Starting Daily Protocol...")
        run_daily_protocol()
        return True

    if choice == "2":
        print("\n>> Setting Up Yearly Goals...")
        from ui.goals_setup import run_goals_wizard

        run_goals_wizard()
        return True

    if choice == "3":
        print("\n>> Viewing Execution Plan...")
        from ui.goals_setup import view_execution_plan

        view_execution_plan()
        return True

    if choice == "4":
        print("\n>> Initiating Morning Awakening...")
        run_awakening_protocol()
        return True

    if choice == "5":
        print("\n>> Entering Private Mode...")
        activate_private_mode()
        return True

    if choice == "6":
        print("\n>> Running Intelligence Brief...")
        try:
            from scrapers.intelligence_service import run_intelligence_brief

            run_intelligence_brief()
        except ModuleNotFoundError as exc:
            print(
                "\nIntelligence Brief requires extra packages. "
                "Run: pip install -r requirements.txt"
            )
            print(f"Missing module: {exc.name}")
        return True

    if choice == "7":
        print("\n>> Starting Awakening Scheduler...")
        print("Press Ctrl+C to stop the scheduler.")
        start_scheduler()
        return True

    if choice == "8":
        print("\n>> Starting Web HUD Dashboard...")
        from dashboard.server import start_server
        start_server()
        return True

    if choice == "9":
        in_dev_menu = True
        while in_dev_menu:
            print_dev_menu()
            dev_choice = input("Enter your choice: ").strip()
            in_dev_menu = handle_dev_choice(dev_choice)
        return True

    if choice == "10":
        print("\n>> Forcing Cloud Sync...")
        from automation.cloud_sync import perform_cloud_sync
        perform_cloud_sync()
        return True

    if choice == "11":
        from ui.treasury_cli import run_treasury_cli
        run_treasury_cli()
        return True

    if choice == "12":
        print("Exiting Apex Ghost menu.")
        return False

    print("Invalid choice. Please select a number from 1 to 12.")
    return True


def main() -> None:
    running = True

    while running:
        print_menu()
        choice = input("Enter your choice: ").strip()
        running = handle_choice(choice)


if __name__ == "__main__":
    main()
