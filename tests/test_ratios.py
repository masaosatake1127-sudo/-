"""
財務比率計算のテスト
"""

import pytest
from financial_analysis.models import IncomeStatement, BalanceSheet, CashFlowStatement
from financial_analysis.ratios import FinancialRatios


def make_base_data():
    is_ = IncomeStatement(
        revenue=100_000,
        cost_of_goods_sold=40_000,
        selling_expenses=15_000,
        general_admin_expenses=5_000,
        non_operating_expenses=2_000,  # 支払利息
        income_tax=8_000,
    )
    bs = BalanceSheet(
        cash_and_equivalents=10_000,
        accounts_receivable=20_000,
        inventory=10_000,
        other_current_assets=5_000,
        property_plant_equipment=30_000,
        intangible_assets=5_000,
        investments=5_000,
        accounts_payable=8_000,
        short_term_debt=5_000,
        other_current_liabilities=2_000,
        long_term_debt=20_000,
        other_non_current_liabilities=3_000,
        common_stock=20_000,
        retained_earnings=27_000,
    )
    cf = CashFlowStatement(
        net_income=is_.net_income,
        depreciation_amortization=5_000,
        changes_in_working_capital=-1_000,
        capital_expenditures=-8_000,
    )
    return is_, bs, cf


class TestProfitabilityRatios:
    def test_gross_profit_margin(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        p = r.profitability()
        assert abs(p.gross_profit_margin - 60.0) < 0.01

    def test_operating_profit_margin(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        p = r.profitability()
        # gross_profit=60000, op_expenses=20000, op_income=40000
        assert abs(p.operating_profit_margin - 40.0) < 0.01

    def test_roe_calculation(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        p = r.profitability()
        # net_income = 100000 - 40000 - 15000 - 5000 - 2000 - 8000 = 30000
        # total_equity = 20000 + 27000 = 47000
        expected_roe = (30_000 / 47_000) * 100
        assert abs(p.return_on_equity - expected_roe) < 0.01


class TestSafetyRatios:
    def test_current_ratio(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        s = r.safety()
        # current_assets = 45000, current_liabilities = 15000
        assert abs(s.current_ratio - 300.0) < 0.01

    def test_equity_ratio(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        s = r.safety()
        # total_equity = 47000, total_assets = 85000
        expected = (47_000 / 85_000) * 100
        assert abs(s.equity_ratio - expected) < 0.01

    def test_interest_coverage(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        s = r.safety()
        # operating_income = 40000, interest = 2000
        assert s.interest_coverage_ratio is not None
        assert abs(s.interest_coverage_ratio - 20.0) < 0.01


class TestEfficiencyRatios:
    def test_asset_turnover(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        e = r.efficiency()
        # revenue=100000 / total_assets=85000
        expected = 100_000 / 85_000
        assert abs(e.asset_turnover - expected) < 0.001

    def test_inventory_turnover(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        e = r.efficiency()
        # cogs=40000 / inventory=10000
        assert e.inventory_turnover is not None
        assert abs(e.inventory_turnover - 4.0) < 0.01

    def test_days_sales_outstanding(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        e = r.efficiency()
        # receivables_turnover = 100000/20000 = 5, dso = 365/5 = 73
        assert e.days_sales_outstanding is not None
        assert abs(e.days_sales_outstanding - 73.0) < 0.01


class TestGrowthRatios:
    def test_no_previous_data(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        g = r.growth()
        assert g.revenue_growth_rate is None

    def test_growth_with_previous_data(self):
        is_, bs, cf = make_base_data()
        prev_is = IncomeStatement(
            revenue=80_000,
            cost_of_goods_sold=32_000,
            selling_expenses=12_000,
            general_admin_expenses=4_000,
            income_tax=6_000,
        )
        r = FinancialRatios(is_, bs, cf, prev_income_stmt=prev_is)
        g = r.growth()
        # (100000 - 80000) / 80000 * 100 = 25%
        assert g.revenue_growth_rate is not None
        assert abs(g.revenue_growth_rate - 25.0) < 0.01


class TestCashFlowRatios:
    def test_free_cash_flow(self):
        is_, bs, cf = make_base_data()
        r = FinancialRatios(is_, bs, cf)
        cfr = r.cash_flow_ratios()
        # operating_cf = net_income(30000) + da(5000) + wc(-1000) = 34000
        # free_cf = 34000 - 8000 = 26000
        assert abs(cfr.free_cash_flow - 26_000) < 1

    def test_zero_revenue_safe(self):
        """売上ゼロでもゼロ除算が発生しないこと"""
        is_ = IncomeStatement(revenue=0, cost_of_goods_sold=0, income_tax=0)
        bs = BalanceSheet(common_stock=1_000, retained_earnings=0)
        cf = CashFlowStatement()
        r = FinancialRatios(is_, bs, cf)
        cfr = r.cash_flow_ratios()
        assert cfr.operating_cf_margin == 0.0
