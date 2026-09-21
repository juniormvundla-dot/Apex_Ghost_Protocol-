from __future__ import annotations

# Data models and structures for the Apex Ghost Treasury & Arbitrage Protocol.

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

TransactionType = Literal["expense", "income"]
AssetClassification = Literal["asset", "liability", "sustenance", "waste"]


@dataclass
class TreasuryTransaction:
    """
    Represents a single monetary transaction categorized according to
    Robert Kiyosaki's Asset/Liability framework and Elon Musk's First-Principles utility scoring.
    """
    id: int | None
    transaction_date: str
    title: str
    amount: float
    category: str
    transaction_type: TransactionType
    asset_classification: AssetClassification
    necessity_score: int = 5  # 1 (pure waste/impulse) to 10 (life-critical / high-yield productive asset)
    is_recurring: bool = False
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class BudgetRules:
    """
    Billionaire allocation targets:
    - Robert Kiyosaki: Pay Yourself First (min 30% to Asset column before bills)
    - Elon Musk: Zero-Base Frugality (0% Waste tolerance, ruthless overhead pruning)
    """
    monthly_income: float = 30000.0
    currency: str = "R"
    asset_target_pct: float = 30.0       # Productive machinery, investments, skill tools
    sustenance_target_pct: float = 40.0   # Baseline food, shelter, essential utilities
    skill_capital_pct: float = 15.0      # High-leverage education, hardware, computing
    runway_buffer_pct: float = 15.0      # Liquid freedom runway
    waste_tolerance_pct: float = 0.0     # Zero tolerance for depreciating impulses
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class FinancialHealthReport:
    """
    Real-time assessment of burn rate, freedom runway, and billionaire rule compliance.
    """
    currency: str
    monthly_income: float
    total_expenses: float
    net_cashflow: float
    
    # Categorical breakdown
    asset_total: float
    asset_pct: float
    sustenance_total: float
    sustenance_pct: float
    liability_total: float
    liability_pct: float
    waste_total: float
    waste_pct: float
    
    # Metrics
    monthly_burn_rate: float
    runway_months: float
    kiyosaki_ratio: float           # Assets / (Liabilities + Waste)
    musk_frugality_score: float      # 0 to 100 based on zero-waste discipline
    rule_violations: list[str] = field(default_factory=list)


@dataclass
class MarketOpportunity:
    """
    An identified industry loophole, market gap, or high-margin service solution
    scanned from real-time trends and synthesized by Gemini Pro.
    """
    id: int | None
    title: str
    industry: str
    loophole_summary: str
    service_solution: str
    target_client: str
    pricing_model: str
    action_steps: list[str] = field(default_factory=list)
    status: str = "scanned"          # 'scanned', 'accepted', 'archived'
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
