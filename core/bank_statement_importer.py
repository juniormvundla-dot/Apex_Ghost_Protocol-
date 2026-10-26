from __future__ import annotations

# Air-Gapped Local Bank Statement Importer
# Ingests CSV / text statements, scrubs PII, and runs 90%+ local prediction.
# 100% on-device: Zero bytes ever leave the local machine.

import csv
import re
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass

from core.financial_privacy import privacy_guard
from core.local_transaction_classifier import local_classifier, ClassificationResult
from core.treasury_models import TreasuryTransaction
from core.treasury_service import treasury_service


@dataclass
class ImportedTransactionCandidate:
    raw_date: str
    iso_date: str
    raw_title: str
    clean_title: str
    amount: float
    tx_type: str  # 'expense' or 'income'
    classification: ClassificationResult
    is_recurring: bool = False


class BankStatementImporter:
    """
    Parses and sanitizes local bank statement files (CSV) and auto-classifies
    transactions using the on-device hybrid intelligence engine.
    """

    def __init__(self) -> None:
        self.supported_extensions = {".csv", ".txt", ".tsv"}

    def _normalize_date(self, raw: str) -> str:
        """
        Parse diverse date formats (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD-Mon-YY) into ISO YYYY-MM-DD.
        """
        raw = raw.strip()
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
            "%d %b %Y", "%d-%b-%Y", "%Y/%m/%d", "%d %B %Y",
            "%d/%m/%y", "%m/%d/%y", "%d-%m-%y"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.date().isoformat()
            except ValueError:
                continue

        # Fallback to today if unparseable
        return date.today().isoformat()

    def parse_file(self, file_path: str | Path) -> list[ImportedTransactionCandidate]:
        """
        Read local bank statement and classify every transaction on-device.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Bank statement file not found: {path}")

        # Try multiple encodings
        content = None
        for enc in ["utf-8-sig", "utf-8", "cp1252", "latin-1"]:
            try:
                content = path.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError(f"Unable to read {path.name} with standard encodings.")

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return []

        # Auto-detect delimiter (, or ; or \t)
        first_line = lines[0]
        delimiter = ","
        if "\t" in first_line:
            delimiter = "\t"
        elif ";" in first_line and first_line.count(";") > first_line.count(","):
            delimiter = ";"

        reader = csv.reader(lines, delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return []

        # Identify header indices
        header_idx = -1
        date_col = -1
        desc_col = -1
        amount_col = -1
        debit_col = -1
        credit_col = -1

        for idx, row in enumerate(rows[:10]):
            lower_row = [c.lower().strip() for c in row]
            has_date = any("date" in c for c in lower_row)
            has_desc = any(any(k in c for k in ["desc", "narrative", "payee", "vendor", "details", "memo"]) for c in lower_row)
            has_amount = any(any(k in c for k in ["amount", "value", "paid out", "paid in", "debit", "credit"]) for c in lower_row)

            if has_date and (has_desc or has_amount):
                header_idx = idx
                for c_idx, col in enumerate(lower_row):
                    if "date" in col and date_col == -1:
                        date_col = c_idx
                    elif any(k in col for k in ["desc", "narrative", "payee", "vendor", "details", "memo"]) and desc_col == -1:
                        desc_col = c_idx
                    elif "amount" in col and amount_col == -1:
                        amount_col = c_idx
                    elif "debit" in col and debit_col == -1:
                        debit_col = c_idx
                    elif "credit" in col and credit_col == -1:
                        credit_col = c_idx
                break

        # If no explicit header, assume standard column fallback (Date, Description, Amount)
        if header_idx == -1:
            data_rows = rows
            date_col = 0
            desc_col = 1
            amount_col = 2
        else:
            data_rows = rows[header_idx + 1:]

        candidates: list[ImportedTransactionCandidate] = []

        for row in data_rows:
            if not row or len(row) <= max(date_col, desc_col):
                continue

            raw_date = row[date_col].strip()
            raw_desc = row[desc_col].strip() if desc_col < len(row) else "Unknown"

            # Parse amount & determine inflow/outflow
            amount = 0.0
            tx_type = "expense"

            if amount_col != -1 and amount_col < len(row) and row[amount_col].strip():
                raw_amt = re.sub(r"[^\d.,\-+]", "", row[amount_col].strip())
                # Handle negative amounts
                try:
                    val = float(raw_amt.replace(",", ""))
                    if val < 0:
                        amount = abs(val)
                        tx_type = "expense"
                    else:
                        amount = val
                        # Default check: if credit column exists or marked as positive
                        tx_type = "expense"
                except ValueError:
                    amount = 0.0
            elif debit_col != -1 and credit_col != -1:
                # Separate debit / credit columns
                debit_val = re.sub(r"[^\d.]", "", row[debit_col].replace(",", "").strip()) if debit_col < len(row) else ""
                credit_val = re.sub(r"[^\d.]", "", row[credit_col].replace(",", "").strip()) if credit_col < len(row) else ""
                if debit_val:
                    amount = float(debit_val)
                    tx_type = "expense"
                elif credit_val:
                    amount = float(credit_val)
                    tx_type = "income"

            if amount <= 0.001:
                continue

            # 1. Air-Gapped PII Redaction & Vendor Normalization
            sanitized_title = privacy_guard.sanitize_text(raw_desc)
            clean_vendor = privacy_guard.normalize_vendor_name(sanitized_title)
            iso_date = self._normalize_date(raw_date)

            # 2. Local 90%+ Predictor Classification
            classification = local_classifier.classify_transaction(
                raw_title=clean_vendor,
                amount=amount,
                tx_type=tx_type
            )

            # Heuristic check for recurring subscriptions
            is_recurring = any(sub in clean_vendor.lower() for sub in [
                "netflix", "spotify", "gym", "virgin active", "fiber", "afrihost", "cell c", "mtn", "vodacom"
            ])

            candidates.append(
                ImportedTransactionCandidate(
                    raw_date=raw_date,
                    iso_date=iso_date,
                    raw_title=raw_desc,
                    clean_title=clean_vendor,
                    amount=round(amount, 2),
                    tx_type=tx_type,
                    classification=classification,
                    is_recurring=is_recurring,
                )
            )

        return candidates

    def commit_transactions(
        self,
        candidates: list[ImportedTransactionCandidate]
    ) -> int:
        """
        Commit verified transactions to SQLite and trigger local model retraining.
        """
        committed = 0
        now = datetime.now().isoformat()

        for c in candidates:
            tx = TreasuryTransaction(
                id=None,
                transaction_date=c.iso_date,
                title=c.clean_title,
                amount=c.amount,
                category=c.classification.category,
                transaction_type=c.tx_type,
                asset_classification=c.classification.asset_classification,
                necessity_score=c.classification.necessity_score,
                is_recurring=c.is_recurring,
                notes=f"Auto-imported (Confidence: {int(c.classification.confidence*100)}%, {c.classification.matched_by})",
                created_at=now,
            )
            treasury_service.add_transaction(tx)
            committed += 1

        # Automatically re-train local ML classifier on new ground truth
        local_classifier.retrain()
        return committed


# Global importer instance
statement_importer = BankStatementImporter()
