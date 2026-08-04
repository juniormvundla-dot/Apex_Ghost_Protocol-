from __future__ import annotations

# This file filters trend items for cybersecurity relevance.
# It helps Apex Ghost separate general tech trends from security-focused items.
# Later, this can become a smarter classifier or scoring system.

from dataclasses import dataclass, field
from datetime import datetime

from scrapers.trends import TrendItem


SECURITY_KEYWORDS = [
    "security",
    "cybersecurity",
    "vulnerability",
    "exploit",
    "malware",
    "ransomware",
    "breach",
    "patch",
    "zero-day",
    "incident",
    "authentication",
    "authorization",
    "pentest",
    "penetration",
]


@dataclass
class SecurityFinding:
    """
    Represents one trend item that appears security-related.
    """
    item: TrendItem
    matched_keywords: list[str] = field(default_factory=list)
    flagged_at: datetime = field(default_factory=datetime.now)


class SecurityFilter:
    """
    Finds security-related items from a list of trend items.
    """

    def is_security_related(self, text: str) -> list[str]:
        """
        Return a list of matched keywords found in the text.
        """
        text_lower = text.lower()
        matches = [keyword for keyword in SECURITY_KEYWORDS if keyword in text_lower]
        return matches

    def filter_items(self, items: list[TrendItem]) -> list[SecurityFinding]:
        """
        Return only the items that look security-related.
        """
        findings: list[SecurityFinding] = []

        for item in items:
            text = f"{item.title} {item.summary}"
            matches = self.is_security_related(text)

            if matches:
                findings.append(
                    SecurityFinding(
                        item=item,
                        matched_keywords=matches,
                    )
                )

        return findings

    def print_findings(self, findings: list[SecurityFinding]) -> None:
        """
        Print security findings in a readable format.
        """
        print("\n=== SECURITY FINDINGS ===")

        if not findings:
            print("No security-related items found.")
            return

        for index, finding in enumerate(findings, start=1):
            print(f"\n{index}. {finding.item.title}")
            print(f"   Source: {finding.item.source}")
            print(f"   URL: {finding.item.url}")
            print(f"   Matches: {', '.join(finding.matched_keywords)}")
            print(f"   Flagged at: {finding.flagged_at}")


def filter_security_items(items: list[TrendItem]) -> list[SecurityFinding]:
    """
    Convenience function for quick security filtering.
    """
    security_filter = SecurityFilter()
    return security_filter.filter_items(items)


if __name__ == "__main__":
    from scrapers.trends import collect_trends

    items = collect_trends()
    findings = filter_security_items(items)
    SecurityFilter().print_findings(findings)