from __future__ import annotations

# This file connects the scraping pipeline into one intelligence workflow.
# It combines:
# - trend collection
# - trend summarization
# - security filtering
#
# The result is a single daily intelligence brief.

from dataclasses import dataclass
from datetime import datetime

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scrapers.trends import TrendsScraper, TrendItem
from scrapers.summarizer import TrendSummarizer, TrendSummary
from scrapers.security import SecurityFilter, SecurityFinding
from voice.jarvis_brain import generate_intelligence_script
from voice.tts import speak_text


@dataclass
class IntelligenceBrief:
    """
    Represents the final intelligence report for the day.
    """
    generated_at: datetime
    total_items: int
    trend_summary: TrendSummary
    security_findings: list[SecurityFinding]


class IntelligenceService:
    """
    High-level service that gathers and prepares daily intelligence.
    """

    def __init__(self) -> None:
        self.trends_scraper = TrendsScraper()
        self.summarizer = TrendSummarizer()
        self.security_filter = SecurityFilter()

    def collect_items(self) -> list[TrendItem]:
        """
        Collect raw trend items from all sources.
        """
        return self.trends_scraper.scrape_all()

    def build_brief(self) -> IntelligenceBrief:
        """
        Build a complete intelligence brief.
        """
        print("[J.A.R.V.I.S.] Scraping primary intelligence sources...")
        items = self.collect_items()
        print("[J.A.R.V.I.S.] Summarizing collected trends...")
        trend_summary = self.summarizer.summarize(items)
        print("[J.A.R.V.I.S.] Running security threat parsing and filtering...")
        security_findings = self.security_filter.filter_items(items)
        print("[J.A.R.V.I.S.] Report compilation complete.")

        return IntelligenceBrief(
            generated_at=datetime.now(),
            total_items=len(items),
            trend_summary=trend_summary,
            security_findings=security_findings,
        )

    def print_brief(self, brief: IntelligenceBrief) -> None:
        """
        Print the intelligence brief in a readable format.
        """
        print("\n=================================")
        print("      APEX GHOST INTELLIGENCE")
        print("=================================")
        print(f"Generated at: {brief.generated_at}")
        print(f"Total items: {brief.total_items}")

        print("\n--- TREND SUMMARY ---")
        print(brief.trend_summary.content)

        print("\n--- SECURITY FINDINGS ---")
        if not brief.security_findings:
            print("No security-related items found.")
        else:
            self.security_filter.print_findings(brief.security_findings)

    def run(self) -> IntelligenceBrief:
        """
        Run the full intelligence pipeline and print the report.
        """
        brief = self.build_brief()
        self.print_brief(brief)
        
        print("\n[J.A.R.V.I.S.] Synthesizing intelligence for voice assistant...")
        security_text = "\n".join([f"- {f.title}" for f in brief.security_findings]) if brief.security_findings else "No immediate security threats."
        script = generate_intelligence_script(brief.trend_summary.content, security_text)
        
        if script:
            print(f"[J.A.R.V.I.S. Audio Script]: {script}")
            speak_text(script)
            
        return brief


def run_intelligence_brief() -> IntelligenceBrief:
    """
    Convenience function for running the intelligence service quickly.
    """
    service = IntelligenceService()
    return service.run()


if __name__ == "__main__":
    run_intelligence_brief()