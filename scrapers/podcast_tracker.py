from __future__ import annotations

# Zero-dependency RSS parser for podcast releases (Dr. Huberman Lab).
# Uses Python standard libraries to fetch and extract episode intelligence
# for J.A.R.V.I.S. voice briefings without requiring AI or paid API keys.

import email.utils
import ssl
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

HUBERMAN_RSS_URL = "https://feeds.megaphone.fm/hubermanlab"


def fetch_latest_huberman_episode() -> dict[str, str] | None:
    """
    Fetch and parse the Dr. Huberman Lab podcast RSS feed.
    Returns a dict with 'title', 'pub_date_str', and 'age_days' or None on failure.
    """
    req = urllib.request.Request(
        HUBERMAN_RSS_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )

    try:
        # Try standard HTTPS verification first; fall back to unverified SSL context if certificate verification fails
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                xml_data = resp.read()
        except urllib.error.URLError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                    xml_data = resp.read()
            else:
                raise e

        root = ET.fromstring(xml_data)
        item = root.find(".//item")
        if item is None:
            return None

        title_el = item.find("title")
        pubdate_el = item.find("pubDate")

        if title_el is None or title_el.text is None:
            return None

        title = title_el.text.strip()
        pub_date_str = pubdate_el.text.strip() if (pubdate_el is not None and pubdate_el.text) else ""

        age_days = 0
        if pub_date_str:
            try:
                parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
                now_utc = datetime.now(timezone.utc)
                age_days = (now_utc - parsed_date).days
            except Exception:
                age_days = 0

        return {
            "title": title,
            "pub_date_str": pub_date_str,
            "age_days": str(age_days),
        }
    except Exception as exc:
        print(f"[Podcast Tracker] Could not reach Huberman Lab feed: {exc}")
        return None


def get_huberman_voice_update() -> str | None:
    """
    Constructs a J.A.R.V.I.S. formatted voice script segment for the podcast.
    """
    data = fetch_latest_huberman_episode()
    if not data:
        return None

    title = data["title"]
    # Clean common prefixes or extraneous symbols from title for smoother TTS synthesis
    title_clean = title.replace("|", " - ").replace('"', '').strip()
    
    try:
        age = int(data.get("age_days", "0"))
    except ValueError:
        age = 0

    if age <= 7:
        return (
            f"Furthermore, Doctor Andrew Huberman has recently released a fresh neuro-optimization "
            f"protocol titled: {title_clean}."
        )
    else:
        return (
            f"For your daily cognitive focus, the latest available protocol from Doctor Huberman "
            f"is titled: {title_clean}."
        )


if __name__ == "__main__":
    update = get_huberman_voice_update()
    print("Huberman Voice Update:", update or "No update retrieved.")
