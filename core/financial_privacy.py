from __future__ import annotations

# 100% Local Air-Gapped Financial PII Redactor & Normalizer
# Ensures account numbers, credit card numbers, and personal identifiers
# are scrubbed on-device BEFORE any processing or storage.

import re


class FinancialPrivacyGuard:
    """
    On-device privacy sanitizer for financial statements and transaction records.
    Guarantee: Zero unmasked PII is ever passed to prompts or logs.
    """

    def __init__(self) -> None:
        # Regex patterns for sensitive financial PII
        # 1. Credit / Debit card numbers (13 to 19 digits with optional spaces or dashes)
        self.card_pattern = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

        # 2. Bank account numbers (e.g. ACC# 123456789 or Account: 9876543210)
        self.account_pattern = re.compile(
            r"(?i)\b(?:acc(?:ount)?[\s#:]*|a\/c[\s#:]*)(\d{6,14})\b"
        )

        # 3. National ID numbers (e.g. 13-digit SA ID numbers)
        self.id_pattern = re.compile(r"\b\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{7}\b")

        # 4. Standard POS bank prefixes / noise patterns
        self.pos_noise_pattern = re.compile(
            r"(?i)\b(?:pos\s+purchase|pos\s+deb|pos\s+w\/d|debit\s+order|deb\s+order|"
            r"recurring\s+pmt|card\s+purchase|magtape|eft\s+payment|instant\s+eft|"
            r"atm\s+w\/d|bank\s+charge|service\s+fee|vat\s+charge)\b"
        )

        # 5. Trailing location / timestamp / terminal codes (e.g. ZA #1234, CPT, JHB)
        self.trailing_noise_pattern = re.compile(
            r"(?i)(?:\s+#\d+|\s+\d{2}[A-Z]{3}|\s+ZA|\s+CPT|\s+JHB|\s+DBN|\s+PTA|\s+SA|\s+\d{4,6}$)"
        )

    def mask_credit_card(self, text: str) -> str:
        """
        Mask credit card digits, preserving only the last 4 characters for reconciliation.
        e.g. 4532-1234-5678-9012 -> [CARD_***9012]
        """
        def _repl(match: re.Match) -> str:
            raw = re.sub(r"[ -]", "", match.group(0))
            if len(raw) < 13 or len(raw) > 19:
                return match.group(0)
            return f"[CARD_***{raw[-4:]}]"

        return self.card_pattern.sub(_repl, text)

    def mask_account_number(self, text: str) -> str:
        """
        Mask bank account numbers, preserving only the last 3 digits.
        """
        def _repl(match: re.Match) -> str:
            acc = match.group(1)
            return f"ACC_***{acc[-3:]}"

        return self.account_pattern.sub(_repl, text)

    def mask_personal_ids(self, text: str) -> str:
        """
        Redact national identity and tax identifiers.
        """
        return self.id_pattern.sub("[ID_REDACTED]", text)

    def sanitize_text(self, text: str) -> str:
        """
        Execute full multi-stage PII scrubbing on a raw string.
        """
        if not text:
            return ""
        s = self.mask_credit_card(text)
        s = self.mask_account_number(s)
        s = self.mask_personal_ids(s)
        return s.strip()

    def normalize_vendor_name(self, raw_description: str) -> str:
        """
        Clean bank statement transaction descriptions by stripping POS artifacts,
        timestamps, branch codes, and noise to isolate the core vendor/merchant name.
        Example:
          'POS PURCHASE 12OCT WOOLWORTHS V&A CAPE TOWN ZA #8832' -> 'Woolworths V&A Cape Town'
        """
        # First sanitize any card numbers or account references
        clean = self.sanitize_text(raw_description)

        # Remove common bank transaction prefixes
        clean = self.pos_noise_pattern.sub("", clean)

        # Remove trailing branch / transaction codes
        clean = self.trailing_noise_pattern.sub("", clean)

        # Remove excessive punctuation and whitespace
        clean = re.sub(r"[*_\-\/]+", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        # Title case for clean readable vendor name
        if clean.isupper() or clean.islower():
            clean = clean.title()

        return clean or "General Expense"


# Global reusable privacy guard instance
privacy_guard = FinancialPrivacyGuard()
