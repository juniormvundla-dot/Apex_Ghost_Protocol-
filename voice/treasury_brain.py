from __future__ import annotations

# AI Financial Auditor powered by Gemini Pro / Flash.
# Evaluates spending through Elon Musk's First-Principles and Robert Kiyosaki's Asset-First doctrine.

import os
import requests
from core.config import config
from core.treasury_models import FinancialHealthReport, TreasuryTransaction


def build_deterministic_audit(report: FinancialHealthReport, transactions: list[TreasuryTransaction]) -> str:
    """
    Fallback deterministic financial audit when Gemini API key is absent or offline.
    """
    lines = [
        "### 🏛️ APEX TREASURY AUDIT (DETERMINISTIC FIRST-PRINCIPLES)",
        f"- **Monthly Income**: {report.currency}{report.monthly_income:,.2f}",
        f"- **Total Outflow**: {report.currency}{report.total_expenses:,.2f}",
        f"- **Net Cashflow**: {report.currency}{report.net_cashflow:,.2f}",
        f"- **Kiyosaki Ratio**: {report.kiyosaki_ratio:.2f} (Assets / Bad Outflow)",
        f"- **Musk Frugality Score**: {report.musk_frugality_score}/100",
        f"- **Liquid Freedom Runway**: {report.runway_months} months",
        "",
        "#### 🔍 Capital Allocation Breakdown:",
        f"- 🟢 **Assets (Productive Capital)**: {report.currency}{report.asset_total:,.2f} ({report.asset_pct}%)",
        f"- 🔵 **Sustenance (Core Living)**: {report.currency}{report.sustenance_total:,.2f} ({report.sustenance_pct}%)",
        f"- 🟡 **Liabilities (Draining Overhead)**: {report.currency}{report.liability_total:,.2f} ({report.liability_pct}%)",
        f"- 🔴 **Waste & Impulse**: {report.currency}{report.waste_total:,.2f} ({report.waste_pct}%)",
        "",
    ]

    if report.waste_total > 0:
        lines.append("#### ⚠️ First-Principles Leakage Detected:")
        waste_items = [t for t in transactions if t.asset_classification == "waste"]
        for w in waste_items[:5]:
            lines.append(f"- **{w.title}**: {report.currency}{w.amount:,.2f} (Necessity: {w.necessity_score}/10)")
        lines.append(
            f"\n**Elon Musk Protocol**: Delete all non-essential expenditures immediately. Reallocate {report.currency}{report.waste_total:,.2f} into productive machinery."
        )
    else:
        lines.append("#### ✅ Clean Ledger: Zero waste leakage recorded.")

    if report.asset_pct < 30.0:
        lines.append(
            f"\n#### ⚡ Robert Kiyosaki Directive: You are allocating only {report.asset_pct}% to assets (Target: 30%+). Pay yourself first before paying landlords, subscriptions, and suppliers."
        )

    return "\n".join(lines)


def generate_spending_audit(report: FinancialHealthReport, transactions: list[TreasuryTransaction]) -> str:
    """
    Query Gemini Pro to conduct a rigorous, first-principles billionaire financial audit.
    """
    api_key = getattr(config.private_mode, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return build_deterministic_audit(report, transactions)

    model = getattr(config.private_mode, "gemini_model", "gemini-2.0-flash")

    headers = {"Content-Type": "application/json"}
    if api_key.startswith("AQ."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers["Authorization"] = f"Bearer {api_key}"
        headers["x-goog-api-key"] = api_key
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Prepare transaction summary for Gemini
    tx_summary = []
    for t in transactions[:30]:
        tx_summary.append(
            f"- [{t.transaction_type.upper()}] {t.transaction_date} | {t.title}: {report.currency}{t.amount:,.2f} "
            f"({t.category}, Class: {t.asset_classification}, Utility: {t.necessity_score}/10)"
        )

    prompt = (
        "You are the Apex Ghost Chief Financial Officer and Billionaire Auditor. "
        "You combine the ruthless, first-principles cost pruning of Elon Musk with the Cashflow Quadrant and Asset-First discipline of Robert Kiyosaki.\n\n"
        f"Financial Summary:\n"
        f"- Monthly Income Baseline: {report.currency}{report.monthly_income:,.2f}\n"
        f"- Total Outflow: {report.currency}{report.total_expenses:,.2f}\n"
        f"- Net Cashflow: {report.currency}{report.net_cashflow:,.2f}\n"
        f"- Asset Column: {report.currency}{report.asset_total:,.2f} ({report.asset_pct}% of total)\n"
        f"- Core Sustenance: {report.currency}{report.sustenance_total:,.2f} ({report.sustenance_pct}%)\n"
        f"- Liabilities: {report.currency}{report.liability_total:,.2f} ({report.liability_pct}%)\n"
        f"- Waste/Impulse: {report.currency}{report.waste_total:,.2f} ({report.waste_pct}%)\n"
        f"- Runway: {report.runway_months} months\n"
        f"- Kiyosaki Asset/Bad-Debt Ratio: {report.kiyosaki_ratio}\n"
        f"- Musk Frugality Score: {report.musk_frugality_score}/100\n\n"
        f"Recent Transactions:\n" + "\n".join(tx_summary) + "\n\n"
        "Provide a high-conviction, authoritative audit in 3 structured sections:\n"
        "1. **Leakage & Vulnerabilities**: Call out exact transactions or habits representing toxic waste, vampire subscriptions, or lifestyle creep.\n"
        "2. **First-Principles Pruning (The Musk Doctrine)**: Specific orders on what to eliminate, renegotiate, or freeze immediately.\n"
        "3. **Capital Reallocation (The Kiyosaki Doctrine)**: Clear guidance on how to redirect every reclaimed dollar into high-yield assets, tech/skill weapons, and building financial runway.\n\n"
        "Tone: Direct, disciplined, executive, strategic. Do not mince words."
    )

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        if response.status_code != 200:
            return build_deterministic_audit(report, transactions)

        result = response.json()
        candidates = result.get("candidates", [])
        if not candidates:
            return build_deterministic_audit(report, transactions)

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return build_deterministic_audit(report, transactions)

        text = parts[0].get("text", "")
        return text.strip()

    except Exception:
        return build_deterministic_audit(report, transactions)


def generate_treasury_spoken_briefing(report: FinancialHealthReport) -> str:
    """
    Generate a concise spoken update for J.A.R.V.I.S. TTS.
    """
    if report.waste_total > 0:
        return (
            f"Sir, financial audit reports {report.currency}{report.waste_total:,.0f} in capital leakage. "
            f"Your current freedom runway stands at {report.runway_months} months. Discipline is advised."
        )
    return (
        f"Sir, treasury reports zero capital leakage. "
        f"Asset allocation is at {report.asset_pct} percent with {report.runway_months} months of freedom runway."
    )
