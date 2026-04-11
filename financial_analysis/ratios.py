"""
財務比率計算モジュール

収益性・安全性・効率性・成長性の各財務指標を算出します。
"""

from dataclasses import dataclass
from typing import Optional

from .models import IncomeStatement, BalanceSheet, CashFlowStatement


@dataclass
class ProfitabilityRatios:
    """収益性指標"""
    gross_profit_margin: float          # 売上総利益率 (%)
    operating_profit_margin: float      # 営業利益率 (%)
    net_profit_margin: float            # 純利益率 (%)
    return_on_assets: float             # 総資産利益率 ROA (%)
    return_on_equity: float             # 自己資本利益率 ROE (%)
    ebitda_margin: Optional[float]      # EBITDA マージン (%)


@dataclass
class SafetyRatios:
    """安全性指標"""
    current_ratio: float                # 流動比率 (%)
    quick_ratio: float                  # 当座比率 (%)
    debt_to_equity_ratio: float         # 負債資本比率
    equity_ratio: float                 # 自己資本比率 (%)
    interest_coverage_ratio: Optional[float]  # インタレスト・カバレッジ・レシオ


@dataclass
class EfficiencyRatios:
    """効率性指標"""
    asset_turnover: float               # 総資産回転率 (回)
    inventory_turnover: Optional[float] # 棚卸資産回転率 (回)
    receivables_turnover: Optional[float]  # 売掛金回転率 (回)
    days_sales_outstanding: Optional[float]  # 売掛金回収日数 (日)
    days_inventory_outstanding: Optional[float]  # 棚卸資産回転日数 (日)


@dataclass
class GrowthRatios:
    """成長性指標"""
    revenue_growth_rate: Optional[float]          # 売上高成長率 (%)
    operating_income_growth_rate: Optional[float] # 営業利益成長率 (%)
    net_income_growth_rate: Optional[float]       # 純利益成長率 (%)
    total_assets_growth_rate: Optional[float]     # 総資産成長率 (%)


@dataclass
class CashFlowRatios:
    """キャッシュフロー指標"""
    operating_cf_margin: float          # 営業CFマージン (%)
    free_cash_flow: float               # フリーキャッシュフロー
    cash_flow_to_debt: Optional[float]  # 有利子負債キャッシュフロー比率


class FinancialRatios:
    """財務比率を計算するクラス"""

    def __init__(
        self,
        income_stmt: IncomeStatement,
        balance_sheet: BalanceSheet,
        cash_flow: CashFlowStatement,
        prev_income_stmt: Optional[IncomeStatement] = None,
        prev_balance_sheet: Optional[BalanceSheet] = None,
    ):
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow
        self.prev_income_stmt = prev_income_stmt
        self.prev_balance_sheet = prev_balance_sheet

    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> Optional[float]:
        """ゼロ除算を防ぐ安全な除算"""
        if denominator == 0:
            return None
        return numerator / denominator

    def profitability(self) -> ProfitabilityRatios:
        """収益性指標を計算する"""
        is_ = self.income_stmt
        bs = self.balance_sheet
        cf = self.cash_flow

        gross_margin = self._safe_divide(is_.gross_profit, is_.revenue) * 100
        op_margin = self._safe_divide(is_.operating_income, is_.revenue) * 100
        net_margin = self._safe_divide(is_.net_income, is_.revenue) * 100
        roa = self._safe_divide(is_.net_income, bs.total_assets) * 100
        roe = self._safe_divide(is_.net_income, bs.total_equity) * 100

        ebitda = is_.operating_income + cf.depreciation_amortization
        ebitda_margin = self._safe_divide(ebitda, is_.revenue) * 100 if is_.revenue else None

        return ProfitabilityRatios(
            gross_profit_margin=gross_margin or 0.0,
            operating_profit_margin=op_margin or 0.0,
            net_profit_margin=net_margin or 0.0,
            return_on_assets=roa or 0.0,
            return_on_equity=roe or 0.0,
            ebitda_margin=ebitda_margin,
        )

    def safety(self) -> SafetyRatios:
        """安全性指標を計算する"""
        bs = self.balance_sheet
        is_ = self.income_stmt

        current_ratio = (
            self._safe_divide(bs.total_current_assets, bs.total_current_liabilities) * 100
        )
        quick_assets = bs.cash_and_equivalents + bs.accounts_receivable
        quick_ratio = (
            self._safe_divide(quick_assets, bs.total_current_liabilities) * 100
        )
        de_ratio = self._safe_divide(bs.total_liabilities, bs.total_equity)
        equity_ratio = self._safe_divide(bs.total_equity, bs.total_assets) * 100

        # インタレスト・カバレッジ・レシオ（支払利息がある場合）
        interest_expense = is_.non_operating_expenses
        interest_coverage = (
            self._safe_divide(is_.operating_income, interest_expense)
            if interest_expense > 0
            else None
        )

        return SafetyRatios(
            current_ratio=current_ratio or 0.0,
            quick_ratio=quick_ratio or 0.0,
            debt_to_equity_ratio=de_ratio or 0.0,
            equity_ratio=equity_ratio or 0.0,
            interest_coverage_ratio=interest_coverage,
        )

    def efficiency(self) -> EfficiencyRatios:
        """効率性指標を計算する"""
        is_ = self.income_stmt
        bs = self.balance_sheet

        asset_turnover = self._safe_divide(is_.revenue, bs.total_assets)

        inv_turnover = (
            self._safe_divide(is_.cost_of_goods_sold, bs.inventory)
            if bs.inventory > 0
            else None
        )
        days_inv = (365 / inv_turnover) if inv_turnover else None

        rec_turnover = (
            self._safe_divide(is_.revenue, bs.accounts_receivable)
            if bs.accounts_receivable > 0
            else None
        )
        days_sales = (365 / rec_turnover) if rec_turnover else None

        return EfficiencyRatios(
            asset_turnover=asset_turnover or 0.0,
            inventory_turnover=inv_turnover,
            receivables_turnover=rec_turnover,
            days_sales_outstanding=days_sales,
            days_inventory_outstanding=days_inv,
        )

    def growth(self) -> GrowthRatios:
        """成長性指標を計算する（前期データがある場合）"""
        if self.prev_income_stmt is None and self.prev_balance_sheet is None:
            return GrowthRatios(
                revenue_growth_rate=None,
                operating_income_growth_rate=None,
                net_income_growth_rate=None,
                total_assets_growth_rate=None,
            )

        def growth_rate(current: float, previous: float) -> Optional[float]:
            if previous == 0:
                return None
            return ((current - previous) / abs(previous)) * 100

        rev_growth = (
            growth_rate(self.income_stmt.revenue, self.prev_income_stmt.revenue)
            if self.prev_income_stmt
            else None
        )
        op_growth = (
            growth_rate(self.income_stmt.operating_income, self.prev_income_stmt.operating_income)
            if self.prev_income_stmt
            else None
        )
        ni_growth = (
            growth_rate(self.income_stmt.net_income, self.prev_income_stmt.net_income)
            if self.prev_income_stmt
            else None
        )
        assets_growth = (
            growth_rate(self.balance_sheet.total_assets, self.prev_balance_sheet.total_assets)
            if self.prev_balance_sheet
            else None
        )

        return GrowthRatios(
            revenue_growth_rate=rev_growth,
            operating_income_growth_rate=op_growth,
            net_income_growth_rate=ni_growth,
            total_assets_growth_rate=assets_growth,
        )

    def cash_flow_ratios(self) -> CashFlowRatios:
        """キャッシュフロー指標を計算する"""
        is_ = self.income_stmt
        bs = self.balance_sheet
        cf = self.cash_flow

        ocf_margin = (self._safe_divide(cf.operating_cash_flow, is_.revenue) or 0.0) * 100
        free_cf = cf.operating_cash_flow + cf.capital_expenditures  # capexは負値

        total_debt = bs.short_term_debt + bs.long_term_debt
        cf_to_debt = (
            self._safe_divide(cf.operating_cash_flow, total_debt)
            if total_debt > 0
            else None
        )

        return CashFlowRatios(
            operating_cf_margin=ocf_margin or 0.0,
            free_cash_flow=free_cf,
            cash_flow_to_debt=cf_to_debt,
        )
