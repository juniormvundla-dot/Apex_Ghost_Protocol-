from __future__ import annotations

# Command-line interface for the Apex Ghost Treasury & Arbitrage Protocol.
# 100% Air-Gapped Financial Ingestion & Auditing.

from datetime import datetime, date
from pathlib import Path

from core.treasury_models import TreasuryTransaction, BudgetRules
from core.treasury_service import treasury_service
from voice.treasury_brain import generate_spending_audit
from scrapers.opportunity_hunter import opportunity_hunter
from core.bank_statement_importer import statement_importer


def print_treasury_menu() -> None:
    print("\n=================================")
    print("    APEX TREASURY & ARBITRAGE    ")
    print("=================================")
    print("1. View Capital Health & Runway")
    print("2. Quick-Log Single Transaction")
    print("3. Run Air-Gapped CFO Spending Audit (Local Engine)")
    print("4. Import Local Bank Statement (CSV / Air-Gapped 90%+ Predictor)")
    print("5. Scan Industry Loopholes & Opportunities")
    print("6. Accept Opportunity as Active Quest")
    print("7. Configure Monthly Income & Targets")
    print("8. Back to Main Menu")
    print()


def view_health() -> None:
    report = treasury_service.calculate_health_report()
    print("\n---------------------------------")
    print("      CAPITAL HEALTH MATRIX      ")
    print("---------------------------------")
    print(f"Monthly Baseline Income: {report.currency}{report.monthly_income:,.2f}")
    print(f"Total Outflow / Expenses: {report.currency}{report.total_expenses:,.2f}")
    print(f"Net Monthly Cashflow:     {report.currency}{report.net_cashflow:,.2f}")
    print()
    print(f"🟢 Assets Column (Wealth):      {report.currency}{report.asset_total:,.2f} ({report.asset_pct}%) [Target: >=30%]")
    print(f"🔵 Sustenance (Baseline Living): {report.currency}{report.sustenance_total:,.2f} ({report.sustenance_pct}%)")
    print(f"🟡 Liabilities (Draining):      {report.currency}{report.liability_total:,.2f} ({report.liability_pct}%)")
    print(f"🔴 Toxic Waste & Leakage:       {report.currency}{report.waste_total:,.2f} ({report.waste_pct}%) [Target: 0%]")
    print()
    print(f"⏳ Freedom Runway:        {report.runway_months} months")
    print(f"📐 Kiyosaki Ratio:        {report.kiyosaki_ratio:.2f} (Assets / Bad Outflow)")
    print(f"⚡ Musk Frugality Score:  {report.musk_frugality_score}/100")

    if report.rule_violations:
        print("\n--- ⚠️ VIOLATION DETECTIONS ---")
        for v in report.rule_violations:
            print(f"- {v}")


def log_transaction_prompt() -> None:
    print("\n--- Log New Transaction ---")
    title = input("Description/Vendor: ").strip()
    if not title:
        print("Cancelled.")
        return

    try:
        amount = float(input("Amount: ").strip())
    except ValueError:
        print("Invalid amount.")
        return

    tx_type_choice = input("Type: [1] Expense, [2] Income (Default: 1): ").strip()
    tx_type = "income" if tx_type_choice == "2" else "expense"

    if tx_type == "expense":
        print("\nRobert Kiyosaki Asset Classification:")
        print("1. Asset (Puts money in your pocket: tool, course, equipment, investment)")
        print("2. Sustenance (Baseline survival: rent, groceries, core utilities)")
        print("3. Liability (Draining lifestyle item, luxury subscription, depreciating gadget)")
        print("4. Waste (Pure impulse purchase, unnecessary dining out, unused subscription)")
        class_choice = input("Select classification (1-4, Default: 2): ").strip()
        
        mapping = {
            "1": "asset",
            "2": "sustenance",
            "3": "liability",
            "4": "waste"
        }
        classification = mapping.get(class_choice, "sustenance")

        try:
            score_input = input("Necessity Score (1=pure waste, 10=life/revenue critical) [Default: 5]: ").strip()
            score = int(score_input) if score_input else 5
        except ValueError:
            score = 5
    else:
        classification = "asset"
        score = 10

    category = input("Category (e.g., Software, Food, Housing, Freelance) [Default: General]: ").strip() or "General"
    is_rec = input("Is this a recurring monthly bill? (y/n) [Default: n]: ").strip().lower() == "y"

    tx = TreasuryTransaction(
        id=None,
        transaction_date=date.today().strftime("%Y-%m-%d"),
        title=title,
        amount=amount,
        category=category,
        transaction_type=tx_type,
        asset_classification=classification,
        necessity_score=score,
        is_recurring=is_rec,
    )
    tx_id = treasury_service.add_transaction(tx)
    print(f"\n>> Transaction #{tx_id} successfully recorded in Treasury Ledger!")


def run_audit_prompt() -> None:
    print("\n>> Initiating 100% Air-Gapped First-Principles Spending Audit...")
    report = treasury_service.calculate_health_report()
    transactions = treasury_service.get_transactions(limit=50)
    audit_text = generate_spending_audit(report, transactions)
    print("\n" + audit_text + "\n")


def import_bank_statement_prompt() -> None:
    print("\n========================================================")
    print("  LOCAL AIR-GAPPED BANK STATEMENT INGESTION (90%+ PREDICTOR)")
    print("========================================================")
    print("Privacy Guarantee: All PII (cards, acc#s) scrubbed on device.")
    print("Zero financial data will ever leave this computer.\n")

    path_input = input("Enter path to bank statement CSV file (or Enter for 'storage/statement.csv'): ").strip()
    file_path = path_input if path_input else "storage/statement.csv"

    p = Path(file_path)
    if not p.exists():
        print(f"\n[Error] File not found: {p.resolve()}")
        print("Tip: Export your bank statement as CSV and place it in the storage/ directory.")
        return

    try:
        candidates = statement_importer.parse_file(p)
        if not candidates:
            print(f"\nNo valid transactions could be parsed from {p.name}.")
            return

        print(f"\nSuccessfully parsed {len(candidates)} transactions on-device:")
        print("----------------------------------------------------------------------------------------------------")
        print(f"{'#':<3} | {'Date':<10} | {'Clean Vendor':<26} | {'Amount':<10} | {'Category':<16} | {'Class':<10} | {'Conf':<5}")
        print("----------------------------------------------------------------------------------------------------")

        for idx, c in enumerate(candidates, 1):
            cl = c.classification
            conf_str = f"{int(cl.confidence * 100)}%"
            print(
                f"{idx:<3} | {c.iso_date:<10} | {c.clean_title[:25]:<26} | "
                f"R{c.amount:>8,.2f} | {cl.category[:15]:<16} | "
                f"{cl.asset_classification:<10} | {conf_str:<5}"
            )
        print("----------------------------------------------------------------------------------------------------")

        confirm = input(f"\nCommit all {len(candidates)} transactions into Treasury Ledger? [Y/n]: ").strip().lower()
        if confirm in ["", "y", "yes"]:
            committed = statement_importer.commit_transactions(candidates)
            print(f"\n>> SUCCESS: {committed} transactions securely committed to SQLite!")
            print(">> Local ML Classifier retrained on-device with ground-truth records.")
        else:
            print("\nImport cancelled by user. No records were committed.")

    except Exception as e:
        print(f"\n[Import Error] {e}")


def scan_opportunities_prompt() -> None:
    print("\n>> Scanning market trends and synthesizing high-margin arbitrage opportunities...")
    opps = opportunity_hunter.scan_opportunities()
    print(f"\nSuccessfully surfaced {len(opps)} opportunities:\n")
    for idx, opp in enumerate(opps, 1):
        print(f"[{idx}] {opp.title.upper()} ({opp.industry})")
        print(f"    • Loophole: {opp.loophole_summary}")
        print(f"    • Offering: {opp.service_solution}")
        print(f"    • Target:   {opp.target_client}")
        print(f"    • Pricing:  {opp.pricing_model}")
        print()


def accept_opportunity_prompt() -> None:
    opps = treasury_service.get_opportunities(status="scanned")
    if not opps:
        print("\nNo pending scanned opportunities. Run option 5 to scan first.")
        return

    print("\n--- Available Opportunity Contracts ---")
    for idx, opp in enumerate(opps, 1):
        print(f"{idx}. {opp.title} [{opp.pricing_model}]")

    choice = input("\nSelect opportunity number to accept as Quest: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(opps):
            selected = opps[idx]
            created_quests = treasury_service.convert_opportunity_to_quests(selected.id)
            print(f"\n>> CONTRACT ACCEPTED! Generated {len(created_quests)} Quests in Combat Log:")
            for q in created_quests:
                print(f"   [+] {q}")
        else:
            print("Invalid index.")
    except ValueError:
        print("Invalid input.")


def configure_budget_prompt() -> None:
    rules = treasury_service.get_budget_rules()
    print(f"\nCurrent Baseline Income: {rules.currency}{rules.monthly_income:,.2f}")
    new_inc = input(f"Enter new monthly income [Press Enter to keep {rules.monthly_income}]: ").strip()
    if new_inc:
        try:
            rules.monthly_income = float(new_inc)
        except ValueError:
            print("Invalid number.")
            return

    new_curr = input(f"Enter currency symbol [Press Enter to keep '{rules.currency}']: ").strip()
    if new_curr:
        rules.currency = new_curr

    treasury_service.update_budget_rules(rules)
    print(">> Treasury targets updated successfully.")


def run_treasury_cli() -> None:
    running = True
    while running:
        print_treasury_menu()
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            view_health()
        elif choice == "2":
            log_transaction_prompt()
        elif choice == "3":
            run_audit_prompt()
        elif choice == "4":
            import_bank_statement_prompt()
        elif choice == "5":
            scan_opportunities_prompt()
        elif choice == "6":
            accept_opportunity_prompt()
        elif choice == "7":
            configure_budget_prompt()
        elif choice == "8":
            running = False
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run_treasury_cli()
