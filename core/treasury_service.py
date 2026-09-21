from __future__ import annotations

# Core service managing billionaire-grade expenditure rules,
# capital health calculations, and opportunity-to-quest conversion.

import json
from datetime import datetime, date
from storage.db import database_manager
from core.treasury_models import (
    TreasuryTransaction,
    BudgetRules,
    FinancialHealthReport,
    MarketOpportunity,
)
from quests.models import Quest, QuestLevel, QuestCategory, QuestStatus
from storage.repositories import quest_repository


class TreasuryService:
    """
    Coordinates financial tracking, billionaire asset-to-liability ratios,
    Elon Musk first-principles cost pruning, and market opportunity conversions.
    """

    def __init__(self) -> None:
        self.db = database_manager

    def add_transaction(self, tx: TreasuryTransaction) -> int:
        """
        Record a financial inflow or outflow.
        """
        cursor = self.db.execute(
            """
            INSERT INTO treasury_transactions 
            (transaction_date, title, amount, category, transaction_type, asset_classification, necessity_score, is_recurring, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tx.transaction_date,
                tx.title,
                tx.amount,
                tx.category,
                tx.transaction_type,
                tx.asset_classification,
                tx.necessity_score,
                1 if tx.is_recurring else 0,
                tx.notes,
                tx.created_at,
            ),
        )
        return cursor.lastrowid

    def get_transactions(self, limit: int = 100) -> list[TreasuryTransaction]:
        """
        Retrieve logged transactions ordered by date descending.
        """
        rows = self.db.fetch_all(
            """
            SELECT id, transaction_date, title, amount, category, transaction_type, 
                   asset_classification, necessity_score, is_recurring, notes, created_at
            FROM treasury_transactions
            ORDER BY transaction_date DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        transactions = []
        for r in rows:
            transactions.append(
                TreasuryTransaction(
                    id=r["id"],
                    transaction_date=r["transaction_date"],
                    title=r["title"],
                    amount=float(r["amount"]),
                    category=r["category"],
                    transaction_type=r["transaction_type"],
                    asset_classification=r["asset_classification"],
                    necessity_score=int(r["necessity_score"]),
                    is_recurring=bool(r["is_recurring"]),
                    notes=r["notes"] or "",
                    created_at=r["created_at"],
                )
            )
        return transactions

    def get_budget_rules(self) -> BudgetRules:
        """
        Fetch active billionaire budget targets.
        """
        row = self.db.fetch_one(
            """
            SELECT monthly_income, currency, asset_target_pct, sustenance_target_pct, 
                   skill_capital_pct, runway_buffer_pct, waste_tolerance_pct, updated_at
            FROM treasury_budget_rules
            WHERE id = 1
            """
        )
        if not row:
            return BudgetRules()
        return BudgetRules(
            monthly_income=float(row["monthly_income"]),
            currency=row["currency"],
            asset_target_pct=float(row["asset_target_pct"]),
            sustenance_target_pct=float(row["sustenance_target_pct"]),
            skill_capital_pct=float(row["skill_capital_pct"]),
            runway_buffer_pct=float(row["runway_buffer_pct"]),
            waste_tolerance_pct=float(row["waste_tolerance_pct"]),
            updated_at=row["updated_at"],
        )

    def update_budget_rules(self, rules: BudgetRules) -> None:
        """
        Update budget rules and monthly baseline income.
        """
        self.db.execute(
            """
            UPDATE treasury_budget_rules
            SET monthly_income = ?, currency = ?, asset_target_pct = ?, sustenance_target_pct = ?,
                skill_capital_pct = ?, runway_buffer_pct = ?, waste_tolerance_pct = ?, updated_at = ?
            WHERE id = 1
            """,
            (
                rules.monthly_income,
                rules.currency,
                rules.asset_target_pct,
                rules.sustenance_target_pct,
                rules.skill_capital_pct,
                rules.runway_buffer_pct,
                rules.waste_tolerance_pct,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    def calculate_health_report(self) -> FinancialHealthReport:
        """
        Analyze current expenses against billionaire allocation targets:
        - Robert Kiyosaki: Pay yourself first (>= 30% to Assets)
        - Elon Musk: First-Principles Zero-Base Waste elimination
        """
        rules = self.get_budget_rules()
        transactions = self.get_transactions(limit=300)

        income_logged = sum(t.amount for t in transactions if t.transaction_type == "income")
        effective_income = max(rules.monthly_income, income_logged)

        asset_total = 0.0
        sustenance_total = 0.0
        liability_total = 0.0
        waste_total = 0.0

        for t in transactions:
            if t.transaction_type == "expense":
                if t.asset_classification == "asset":
                    asset_total += t.amount
                elif t.asset_classification == "sustenance":
                    sustenance_total += t.amount
                elif t.asset_classification == "liability":
                    liability_total += t.amount
                elif t.asset_classification == "waste":
                    waste_total += t.amount

        total_expenses = asset_total + sustenance_total + liability_total + waste_total
        net_cashflow = effective_income - total_expenses

        denominator = effective_income if effective_income > 0 else max(1.0, total_expenses)
        asset_pct = round((asset_total / denominator) * 100.0, 1)
        sustenance_pct = round((sustenance_total / denominator) * 100.0, 1)
        liability_pct = round((liability_total / denominator) * 100.0, 1)
        waste_pct = round((waste_total / denominator) * 100.0, 1)

        # Monthly burn rate (living overhead + liabilities + recurring waste)
        monthly_burn_rate = sustenance_total + liability_total + waste_total

        # Liquid runway months based on accumulated assets vs monthly burn
        runway_months = round(asset_total / max(1.0, monthly_burn_rate), 1) if monthly_burn_rate > 0 else 12.0

        # Kiyosaki Ratio: Assets vs (Liabilities + Waste)
        bad_outflow = liability_total + waste_total
        kiyosaki_ratio = round(asset_total / max(1.0, bad_outflow), 2)

        # Musk Frugality Score: 100 minus penalty for waste & high liability
        waste_penalty = (waste_total / max(1.0, total_expenses)) * 120.0
        liability_penalty = (liability_total / max(1.0, total_expenses)) * 40.0
        musk_frugality_score = max(0.0, min(100.0, round(100.0 - (waste_penalty + liability_penalty), 1)))

        # Evaluate rule violations
        violations = []
        if waste_total > 0:
            violations.append(
                f"[MUSK FIRST-PRINCIPLES] Detected {rules.currency}{waste_total:,.2f} in waste/impulse leakage. Zero tolerance threshold breached."
            )
        if asset_pct < rules.asset_target_pct:
            violations.append(
                f"[KIYOSAKI RULE] Asset allocation is currently {asset_pct}% (Target: {rules.asset_target_pct}%). You are paying others before paying yourself."
            )
        if liability_pct > 20.0:
            violations.append(
                f"[CASHFLOW WARNING] Liabilities account for {liability_pct}% of capital. Luxury or depreciating items are draining momentum."
            )
        if net_cashflow < 0:
            violations.append(
                f"[CRITICAL DEFICIT] Net cashflow is negative ({rules.currency}{net_cashflow:,.2f}). Burn rate exceeds monthly capital generation."
            )

        return FinancialHealthReport(
            currency=rules.currency,
            monthly_income=effective_income,
            total_expenses=total_expenses,
            net_cashflow=net_cashflow,
            asset_total=asset_total,
            asset_pct=asset_pct,
            sustenance_total=sustenance_total,
            sustenance_pct=sustenance_pct,
            liability_total=liability_total,
            liability_pct=liability_pct,
            waste_total=waste_total,
            waste_pct=waste_pct,
            monthly_burn_rate=monthly_burn_rate,
            runway_months=runway_months,
            kiyosaki_ratio=kiyosaki_ratio,
            musk_frugality_score=musk_frugality_score,
            rule_violations=violations,
        )

    # ── Opportunity Hunter Operations ──────────────────────────────────────────

    def save_opportunity(self, opp: MarketOpportunity) -> int:
        """
        Store a scanned opportunity blueprint in SQLite.
        """
        cursor = self.db.execute(
            """
            INSERT INTO market_opportunities
            (title, industry, loophole_summary, service_solution, target_client, pricing_model, action_steps, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                opp.title,
                opp.industry,
                opp.loophole_summary,
                opp.service_solution,
                opp.target_client,
                opp.pricing_model,
                json.dumps(opp.action_steps),
                opp.status,
                opp.created_at,
            ),
        )
        opp.id = cursor.lastrowid
        return cursor.lastrowid

    def get_opportunities(self, status: str | None = None) -> list[MarketOpportunity]:
        """
        Fetch market opportunities, optionally filtered by status.
        """
        if status:
            rows = self.db.fetch_all(
                """
                SELECT id, title, industry, loophole_summary, service_solution, 
                       target_client, pricing_model, action_steps, status, created_at
                FROM market_opportunities
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,),
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT id, title, industry, loophole_summary, service_solution, 
                       target_client, pricing_model, action_steps, status, created_at
                FROM market_opportunities
                ORDER BY id DESC
                """
            )

        results = []
        for r in rows:
            steps = []
            if r["action_steps"]:
                try:
                    steps = json.loads(r["action_steps"])
                except Exception:
                    steps = []
            results.append(
                MarketOpportunity(
                    id=r["id"],
                    title=r["title"],
                    industry=r["industry"],
                    loophole_summary=r["loophole_summary"],
                    service_solution=r["service_solution"],
                    target_client=r["target_client"],
                    pricing_model=r["pricing_model"],
                    action_steps=steps,
                    status=r["status"],
                    created_at=r["created_at"],
                )
            )
        return results

    def convert_opportunity_to_quests(self, opp_id: int) -> list[str]:
        """
        Convert a scanned business loophole/opportunity into an active Apex Ghost quest contract!
        Creates 3 sequential quests in the Combat Log:
        1. Prototype MVP / Service Blueprint
        2. Direct Outreach / 5 Pitches
        3. Close First Client (Boss Quest with 1000 XP)
        """
        row = self.db.fetch_one(
            "SELECT * FROM market_opportunities WHERE id = ?", (opp_id,)
        )
        if not row:
            return []

        title = row["title"]
        solution = row["service_solution"]
        target = row["target_client"]
        pricing = row["pricing_model"]

        today = date.today()
        created_titles = []

        # 1. Prototype MVP Quest (Daily)
        q1_title = f"[ARBITRAGE] Prototype Solution: {title}"
        q1 = Quest(
            title=q1_title,
            description=f"Build prototype / MVP deliverable for: {solution}. Target: {target}.",
            level=QuestLevel.DAILY,
            category=QuestCategory.SIDE,
            target_date=today,
            xp_reward=150,
            difficulty=3,
        )
        quest_repository.save_quest(q1)
        created_titles.append(q1_title)

        # 2. Prospect Outreach Quest (Daily)
        q2_title = f"[ARBITRAGE] Prospect Outreach: 5 pitches for {title}"
        q2 = Quest(
            title=q2_title,
            description=f"Reach out to 5 prospective clients matching '{target}' offering solution at {pricing}.",
            level=QuestLevel.DAILY,
            category=QuestCategory.CORE,
            target_date=today,
            xp_reward=250,
            difficulty=4,
        )
        quest_repository.save_quest(q2)
        created_titles.append(q2_title)

        # 3. Boss Quest: Close First Client
        q3_title = f"[BOSS] [ARBITRAGE] Close First Paying Client for {title}"
        q3 = Quest(
            title=q3_title,
            description=f"Secure contract and deliver initial milestone for {title}. Price model: {pricing}.",
            level=QuestLevel.WEEKLY,
            category=QuestCategory.BOSS,
            target_date=today,
            xp_reward=1000,
            difficulty=5,
            evidence_required=True,
        )
        quest_repository.save_quest(q3)
        created_titles.append(q3_title)

        # Mark opportunity as accepted
        self.db.execute(
            "UPDATE market_opportunities SET status = 'accepted' WHERE id = ?",
            (opp_id,),
        )

        return created_titles


treasury_service = TreasuryService()
