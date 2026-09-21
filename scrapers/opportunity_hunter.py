from __future__ import annotations

# Industry loophole & market opportunity scanner.
# Pairs live web scrapers with Gemini Pro to identify high-margin service/software opportunities.

import os
import json
import re
import requests
from datetime import datetime
from core.config import config
from core.treasury_models import MarketOpportunity
from core.treasury_service import treasury_service
from scrapers.trends import TrendsScraper, TrendItem


CURATED_BLUEPRINTS = [
    {
        "title": "B2B Autonomous Workflow & AI Integration Engine",
        "industry": "Artificial Intelligence / Enterprise Ops",
        "loophole_summary": "Legacy enterprises and agencies spend $10,000+/mo on manual data entry and customer triage because large consulting firms over-engineer custom software.",
        "service_solution": "Deploy lightweight Python/Gemini middleware that automatically connects CRM forms, extracts document data, and triggers Slack/Email notifications.",
        "target_client": "Mid-sized law firms, real estate brokerages, accounting practices.",
        "pricing_model": "$2,500 one-time setup + $450/mo maintenance/support.",
        "action_steps": [
            "Build a plug-and-play Python webhook listening to Google Forms/Stripe.",
            "Write a cold email offering a 7-day free operational pilot.",
            "Pitch 10 local accounting and legal practices."
        ]
    },
    {
        "title": "Local Service Autonomous Booking & Missed-Call Recovery Bot",
        "industry": "Local SMB / Lead Generation",
        "loophole_summary": "62% of calls to local contractors (plumbers, HVAC, electricians) go to voicemail while they are on job sites, losing thousands in high-ticket emergency jobs.",
        "service_solution": "Set up an instant SMS auto-responder that engages missed calls via conversational AI and schedules visits directly into Google Calendar.",
        "target_client": "Emergency plumbers, electricians, roofing contractors.",
        "pricing_model": "$1,000 setup + $300/month or $50 per confirmed booking.",
        "action_steps": [
            "Configure Twilio SMS webhook to auto-reply within 10 seconds of a missed call.",
            "Integrate Gemini API for conversational slot booking.",
            "Demo system to 5 local home contractors."
        ]
    },
    {
        "title": "Cloud Infrastructure & Database Cost-Pruning Audit",
        "industry": "Cloud SaaS / DevOps",
        "loophole_summary": "Startups blindly accumulate idle AWS/GCP resources, unattached EBS volumes, and oversized RDS instances, wasting 25-40% of their monthly cloud bill.",
        "service_solution": "Offer a zero-risk 48-hour Cloud Waste Audit using Boto3 scripts. Charge 30% of verified annualized savings.",
        "target_client": "Funded seed/Series-A tech startups with $3k - $20k monthly cloud spend.",
        "pricing_model": "Performance fee: 30% of first-year realized savings.",
        "action_steps": [
            "Package a read-only IAM auditing script that flags zombie instances and unindexed storage.",
            "Generate sample PDF audit report.",
            "Direct message 15 startup CTOs on LinkedIn or GitHub."
        ]
    }
]


class OpportunityHunter:
    """
    Scans live market signals and generates actionable service/software arbitrage opportunities.
    """

    def __init__(self) -> None:
        self.trends_scraper = TrendsScraper()

    def scan_opportunities(self) -> list[MarketOpportunity]:
        """
        Execute market scan and return fresh opportunity blueprints.
        """
        print("[J.A.R.V.I.S. Treasury] Gathering real-time market trends and technology movements...")
        try:
            trend_items = self.trends_scraper.scrape_all()
        except Exception as exc:
            print(f"[J.A.R.V.I.S. Treasury] Scraper notice: {exc}. Proceeding with core intelligence.")
            trend_items = []

        opportunities = self._synthesize_with_gemini(trend_items)

        # Persist new opportunities to SQLite
        for opp in opportunities:
            treasury_service.save_opportunity(opp)

        return opportunities

    def _synthesize_with_gemini(self, trend_items: list[TrendItem]) -> list[MarketOpportunity]:
        api_key = getattr(config.private_mode, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("[J.A.R.V.I.S. Treasury] Gemini API key not detected. Deploying curated billionaire blueprints.")
            return self._fallback_blueprints()

        model = getattr(config.private_mode, "gemini_model", "gemini-2.0-flash")
        headers = {"Content-Type": "application/json"}
        if api_key.startswith("AQ."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers["Authorization"] = f"Bearer {api_key}"
            headers["x-goog-api-key"] = api_key
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        trends_context = "\n".join([f"- {t.title} ({t.source})" for t in trend_items[:15]])

        prompt = (
            "You are the Apex Ghost Chief Arbitrage Officer and Billionaire Strategist. "
            "Your objective is to identify market loopholes, operational bottlenecks, and high-margin services "
            "that a high-agency developer or solo technical operator can monetize immediately.\n\n"
            f"Current Market Trends & Signals:\n{trends_context}\n\n"
            "Analyze these shifts and synthesize exactly 3 concrete, high-leverage service or micro-SaaS opportunities. "
            "For each opportunity, identify a structural market inefficiency (the loophole) where traditional agencies or businesses "
            "are slow or wasteful, and explain how to offer a targeted solution.\n\n"
            "Output strictly valid JSON with this exact schema (no markdown blocks, no prefix text):\n"
            "[\n"
            "  {\n"
            "    \"title\": \"Descriptive name of the offering\",\n"
            "    \"industry\": \"Industry/Category\",\n"
            "    \"loophole_summary\": \"The specific market inefficiency or friction point\",\n"
            "    \"service_solution\": \"The exact technical system or service to offer\",\n"
            "    \"target_client\": \"Specific target buyer persona\",\n"
            "    \"pricing_model\": \"Pricing structure (e.g. $2,000 setup + $400/mo)\",\n"
            "    \"action_steps\": [\"Step 1\", \"Step 2\", \"Step 3\"]\n"
            "  }\n"
            "]"
        )

        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=25)
            if response.status_code == 200:
                result = response.json()
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                # Clean potential markdown wrapping
                clean_json = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json.strip(), flags=re.MULTILINE)

                parsed = json.loads(clean_json)
                opportunities = []
                for item in parsed:
                    opportunities.append(
                        MarketOpportunity(
                            id=None,
                            title=item.get("title", "High-Margin Opportunity"),
                            industry=item.get("industry", "Technology"),
                            loophole_summary=item.get("loophole_summary", ""),
                            service_solution=item.get("service_solution", ""),
                            target_client=item.get("target_client", "B2B Clients"),
                            pricing_model=item.get("pricing_model", "Retainer"),
                            action_steps=item.get("action_steps", []),
                        )
                    )
                if opportunities:
                    return opportunities

        except Exception as exc:
            print(f"[J.A.R.V.I.S. Treasury] AI Market Synthesis notice: {exc}. Utilizing battle-tested blueprints.")

        return self._fallback_blueprints()

    def _fallback_blueprints(self) -> list[MarketOpportunity]:
        blueprints = []
        for b in CURATED_BLUEPRINTS:
            blueprints.append(
                MarketOpportunity(
                    id=None,
                    title=b["title"],
                    industry=b["industry"],
                    loophole_summary=b["loophole_summary"],
                    service_solution=b["service_solution"],
                    target_client=b["target_client"],
                    pricing_model=b["pricing_model"],
                    action_steps=b["action_steps"],
                )
            )
        return blueprints


opportunity_hunter = OpportunityHunter()
