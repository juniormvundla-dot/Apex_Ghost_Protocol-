from __future__ import annotations

# This file collects technology trend information from the web.
# It is a starter scraper for Apex Ghost's intelligence layer.
# Later, it can be improved with:
# - better source selection
# - filtering by relevance
# - scheduling
# - summary generation
# - database storage

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class TrendItem:
    """
    Represents one trend or article that was discovered online.
    """
    title: str
    source: str
    url: str
    summary: str = ""
    collected_at: datetime = field(default_factory=datetime.now)


class TrendsScraper:
    """
    Simple scraper for collecting tech trend items.

    This is a v1 implementation meant to be easy to understand and extend.
    """

    def __init__(self, timeout_seconds: int = 15) -> None:
        self.timeout_seconds = timeout_seconds

        # Starter sources for trends.
        # You can replace or expand these later.
        self.sources: list[dict[str, str]] = [
            {
                "name": "Hacker News",
                "url": "https://news.ycombinator.com/",
            },
            {
                "name": "Dev.to",
                "url": "https://dev.to/t/python",
            },
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/",
            },
        ]

    def fetch_html(self, url: str) -> str:
        """
        Download HTML from a web page.

        For local testing, certificate verification is disabled because
        some networks or environments inject certificates that requests
        cannot validate properly.
        """
        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            verify=False,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        return response.text

    def parse_generic_titles(self, html: str, source_name: str, source_url: str) -> list[TrendItem]:
        """
        Parse a page and return a list of basic TrendItem objects.

        This uses a generic approach:
        - look for headings
        - use the first few as trend items
        """
        soup = BeautifulSoup(html, "html.parser")

        items: list[TrendItem] = []

        # Collect headings in order of appearance
        headings = soup.find_all(["h1", "h2", "h3"])
        for heading in headings[:10]:
            title = heading.get_text(strip=True)
            if not title:
                continue

            items.append(
                TrendItem(
                    title=title,
                    source=source_name,
                    url=source_url,
                    summary="Discovered from page headings.",
                )
            )

        return items

    def scrape_source(self, source: dict[str, str]) -> list[TrendItem]:
        """
        Scrape one source and return a list of trend items.
        """
        name = source["name"]
        url = source["url"]

        try:
            html = self.fetch_html(url)
            return self.parse_generic_titles(html, name, url)

        except Exception as exc:
            print(f"Failed to scrape {name}: {exc}")
            return []

    def scrape_all(self) -> list[TrendItem]:
        """
        Scrape all configured sources.
        """
        all_items: list[TrendItem] = []

        print("[SCANNER] Accessing security and trend channels...")
        for source in self.sources:
            name = source["name"]
            print(f"[SCANNER] Connecting to source feed: {name}...")
            items = self.scrape_source(source)
            print(f"[SCANNER] Found {len(items)} items from {name}")
            all_items.extend(items)

        print(f"[SCANNER] Completed. Total items collected: {len(all_items)}")
        return all_items

    def print_trends(self, items: list[TrendItem]) -> None:
        """
        Print trend items in a readable format.
        """
        print("\n=== TREND REPORT ===")

        if not items:
            print("No trends found.")
            return

        for index, item in enumerate(items, start=1):
            print(f"\n{index}. {item.title}")
            print(f"   Source: {item.source}")
            print(f"   URL: {item.url}")
            print(f"   Collected: {item.collected_at}")


def collect_trends() -> list[TrendItem]:
    """
    Convenience function for collecting trends quickly.
    """
    scraper = TrendsScraper()
    return scraper.scrape_all()


if __name__ == "__main__":
    scraper = TrendsScraper()
    trend_items = scraper.scrape_all()
    scraper.print_trends(trend_items)