from __future__ import annotations

# This file turns raw trend items into a readable summary.
# The goal is to create a simple daily intelligence brief for Apex Ghost.

from dataclasses import dataclass
from datetime import datetime

from scrapers.trends import TrendItem


@dataclass
class TrendSummary:
    """
    Represents a summarized report of scraped trends.
    """
    title: str
    generated_at: datetime
    content: str


class TrendSummarizer:
    """
    Converts scraped trend items into a human-readable summary.
    """

    def summarize(self, items: list[TrendItem]) -> TrendSummary:
        """
        Build a summary from a list of trend items.
        """
        generated_at = datetime.now()

        if not items:
            content = "No trend items were found in this cycle."
            return TrendSummary(
                title="Apex Ghost Trend Brief",
                generated_at=generated_at,
                content=content,
            )

        lines: list[str] = []
        lines.append("Daily Tech Brief")
        lines.append("================")
        lines.append(f"Items collected: {len(items)}")
        lines.append("")

        # Group by source for readability
        source_map: dict[str, list[TrendItem]] = {}
        for item in items:
            source_map.setdefault(item.source, []).append(item)

        for source_name, source_items in source_map.items():
            lines.append(f"Source: {source_name}")
            for item in source_items:
                lines.append(f"- {item.title}")
            lines.append("")

        lines.append("Suggested action:")
        lines.append("- Review the most repeated or strongest themes.")
        lines.append("- Pick one or two topics to study deeper.")
        lines.append("- Ignore noise and low-relevance items.")

        content = "\n".join(lines)

        return TrendSummary(
            title="Apex Ghost Trend Brief",
            generated_at=generated_at,
            content=content,
        )

    def print_summary(self, summary: TrendSummary) -> None:
        """
        Print the summary to the console.
        """
        print("\n=== TREND SUMMARY ===")
        print(f"Title: {summary.title}")
        print(f"Generated at: {summary.generated_at}")
        print()
        print(summary.content)


def build_trend_summary(items: list[TrendItem]) -> TrendSummary:
    """
    Convenience function for building a summary quickly.
    """
    summarizer = TrendSummarizer()
    return summarizer.summarize(items)


if __name__ == "__main__":
    from scrapers.trends import collect_trends

    items = collect_trends()
    summary = build_trend_summary(items)
    TrendSummarizer().print_summary(summary)