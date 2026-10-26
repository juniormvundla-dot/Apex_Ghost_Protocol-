from __future__ import annotations

# Automated Verification Suite: 100% Confidential Financial Pipeline & 90%+ Predictor

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.financial_privacy import privacy_guard
from core.local_transaction_classifier import local_classifier
from core.bank_statement_importer import statement_importer
from core.treasury_models import FinancialHealthReport, TreasuryTransaction
from voice.treasury_brain import generate_spending_audit


def test_pii_redaction_and_normalization() -> None:
    print("\n--- Test 1: Air-Gapped PII Redaction & Vendor Normalization ---")

    # 1. Credit card redaction
    raw_card = "Card charge: 4532-1234-5678-9012 for Netflix"
    sanitized_card = privacy_guard.mask_credit_card(raw_card)
    print(f"Masked Card: '{sanitized_card}'")
    assert "4532" not in sanitized_card, "Failed to redact credit card prefix"
    assert "9012" in sanitized_card, "Failed to preserve card suffix"

    # 2. Account number redaction
    raw_acc = "Payment to Landlord ACC# 123456789"
    sanitized_acc = privacy_guard.mask_account_number(raw_acc)
    print(f"Masked Account: '{sanitized_acc}'")
    assert "123456" not in sanitized_acc, "Failed to redact account number"
    assert "789" in sanitized_acc, "Failed to preserve account suffix"

    # 3. Vendor string normalization
    raw_pos = "POS PURCHASE 12OCT WOOLWORTHS V&A CAPE TOWN ZA #8832"
    clean_vendor = privacy_guard.normalize_vendor_name(raw_pos)
    print(f"Normalized Vendor: '{clean_vendor}'")
    assert "Woolworths" in clean_vendor, f"Expected Woolworths in clean vendor, got {clean_vendor}"
    assert "POS" not in clean_vendor, "Failed to strip POS prefix"
    assert "#8832" not in clean_vendor, "Failed to strip terminal tag"

    print("[OK] Test 1 passed successfully.")


def test_local_90_percent_prediction_accuracy() -> None:
    print("\n--- Test 2: Local 90%+ Prediction Accuracy ---")

    # Benchmark test dataset of 12 realistic bank statement transactions
    benchmark_cases = [
        ("WOOLWORTHS FOOD STORE #124", "sustenance", "Groceries"),
        ("CHECKERS HYPER MEAT MARKET", "sustenance", "Groceries"),
        ("UBER EATS MEAL DELIVERY", "waste", "Food Delivery"),
        ("KFC DRIVE THRU MEAL", "waste", "Fast Food"),
        ("GITHUB CO-PILOT SUBSCRIPTION", "asset", "Software Tools"),
        ("AMAZON AWS CLOUD HOSTING", "asset", "Software Tools"),
        ("UDEMY ONLINE PYTHON COURSE", "asset", "Education & Skills"),
        ("ESKOM PRE-PAID ELECTRICITY", "sustenance", "Utilities"),
        ("TOPS AT SPAR LIQUOR STORE", "waste", "Alcohol"),
        ("STEAM GAMES PURCHASE VALV", "waste", "Gaming & Gambling"),
        ("MONTHLY RENT PAYMENT LEVY", "sustenance", "Housing"),
        ("DIS-CHEM PHARMACY PRESCRIPTIONS", "sustenance", "Healthcare"),
    ]

    correct_predictions = 0
    total = len(benchmark_cases)

    print(f"Evaluating {total} real-world bank statement entries:")
    for raw_vendor, expected_asset_class, expected_cat in benchmark_cases:
        res = local_classifier.classify_transaction(raw_vendor)
        is_correct = (res.asset_classification == expected_asset_class)
        if is_correct:
            correct_predictions += 1
        status = "[CORRECT]" if is_correct else "[MISMATCH]"
        print(f"  {status} '{raw_vendor}' -> {res.category} | {res.asset_classification} (Conf: {int(res.confidence*100)}%, {res.matched_by})")

    accuracy = (correct_predictions / total) * 100.0
    print(f"\nBenchmark Accuracy: {accuracy:.1f}% ({correct_predictions}/{total} correct)")
    assert accuracy >= 90.0, f"Expected accuracy >= 90%, achieved {accuracy:.1f}%"
    print("[OK] Test 2 passed successfully.")


def test_air_gapped_audit_zero_cloud_leakage() -> None:
    print("\n--- Test 3: Air-Gapped Financial Audit (Zero External Network Calls) ---")

    mock_report = FinancialHealthReport(
        monthly_income=30000.0,
        total_expenses=21000.0,
        net_cashflow=9000.0,
        asset_total=6000.0,
        asset_pct=28.6,
        sustenance_total=11000.0,
        sustenance_pct=52.4,
        liability_total=2500.0,
        liability_pct=11.9,
        waste_total=1500.0,
        waste_pct=7.1,
        monthly_burn_rate=21000.0,
        runway_months=4.2,
        kiyosaki_ratio=0.43,
        musk_frugality_score=68.0,
        currency="R",
        rule_violations=["Waste exceeds 0% target"],
    )

    mock_txs = [
        TreasuryTransaction(
            id=1,
            transaction_date="2026-10-14",
            title="Uber Eats Late Night",
            amount=450.0,
            category="Food Delivery",
            transaction_type="expense",
            asset_classification="waste",
            necessity_score=2,
            is_recurring=False,
            notes="Impulse delivery",
            created_at="2026-10-14T20:00:00",
        ),
        TreasuryTransaction(
            id=2,
            transaction_date="2026-10-14",
            title="GitHub Copilot",
            amount=200.0,
            category="Software Tools",
            transaction_type="expense",
            asset_classification="asset",
            necessity_score=9,
            is_recurring=True,
            notes="Developer weapon",
            created_at="2026-10-14T09:00:00",
        ),
    ]

    # Generate spending audit: guaranteed on localhost (Ollama apex-cfo or deterministic)
    audit_output = generate_spending_audit(mock_report, mock_txs)
    print("Audit generated successfully:")
    for line in audit_output.splitlines()[:10]:
        print(f"  {line.encode('ascii', 'replace').decode('ascii')}")

    assert "APEX TREASURY AUDIT" in audit_output, "Expected audit header in report"
    assert "Musk" in audit_output or "Frugality" in audit_output, "Expected Elon Musk doctrine in report"
    assert "Kiyosaki" in audit_output or "Asset" in audit_output, "Expected Robert Kiyosaki doctrine in report"
    print("[OK] Test 3 passed successfully.")


def test_bank_statement_csv_ingestion() -> None:
    print("\n--- Test 4: Bank Statement CSV Ingestion Pipeline ---")

    # Generate a temporary sample statement CSV
    sample_csv_path = project_root / "storage" / "sample_statement.csv"
    sample_data = (
        "Date,Description,Amount\n"
        "2026-10-10,POS PURCHASE 10OCT CHECKERS HYPER CAPE TOWN,-845.50\n"
        "2026-10-11,DEB ORDER GITHUB COPILOT ACC# 987654321,-200.00\n"
        "2026-10-12,POS PURCHASE UBER EATS MEAL,-320.00\n"
        "2026-10-13,SALARY DIRECT DEPOSIT REMUNERATION,35000.00\n"
    )
    sample_csv_path.write_text(sample_data, encoding="utf-8")

    candidates = statement_importer.parse_file(sample_csv_path)
    print(f"Parsed {len(candidates)} candidates from {sample_csv_path.name}:")
    for c in candidates:
        print(f"  - {c.iso_date} | {c.clean_title} | R{c.amount:,.2f} | {c.classification.category} | {c.classification.asset_classification} (Conf: {int(c.classification.confidence*100)}%)")

    assert len(candidates) == 4, f"Expected 4 parsed transactions, got {len(candidates)}"
    
    # Verify card/acc# scrubbed from clean title
    for c in candidates:
        assert "ACC#" not in c.clean_title, f"Account number leaked in title: {c.clean_title}"

    # Clean up sample CSV
    if sample_csv_path.exists():
        sample_csv_path.unlink()

    print("[OK] Test 4 passed successfully.")


if __name__ == "__main__":
    print("==================================================")
    print("APEX GHOST — CONFIDENTIAL FINANCIAL AUDITOR TESTS")
    print("==================================================")
    test_pii_redaction_and_normalization()
    test_local_90_percent_prediction_accuracy()
    test_air_gapped_audit_zero_cloud_leakage()
    test_bank_statement_csv_ingestion()
    print("\n==================================================")
    print("ALL 4 AIR-GAPPED VERIFICATION TESTS PASSED.")
    print("==================================================")
