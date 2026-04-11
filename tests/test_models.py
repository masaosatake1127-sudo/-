"""
財務諸表データモデルのテスト
"""

import pytest
from financial_analysis.models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
)


class TestIncomeStatement:
    def test_auto_calculation(self):
        is_ = IncomeStatement(
            revenue=10_000,
            cost_of_goods_sold=6_000,
            selling_expenses=1_000,
            general_admin_expenses=500,
            income_tax=500,
        )
        assert is_.gross_profit == 4_000
        assert is_.operating_expenses == 1_500
        assert is_.operating_income == 2_500
        assert is_.ordinary_income == 2_500
        assert is_.income_before_tax == 2_500
        assert is_.net_income == 2_000

    def test_non_operating_items(self):
        is_ = IncomeStatement(
            revenue=10_000,
            cost_of_goods_sold=5_000,
            selling_expenses=1_000,
            general_admin_expenses=500,
            non_operating_income=200,
            non_operating_expenses=100,
            income_tax=0,
        )
        assert is_.operating_income == 3_500
        assert is_.ordinary_income == 3_600  # 3500 + 200 - 100

    def test_extraordinary_items(self):
        is_ = IncomeStatement(
            revenue=10_000,
            cost_of_goods_sold=5_000,
            selling_expenses=0,
            general_admin_expenses=0,
            extraordinary_income=500,
            extraordinary_losses=1_000,
            income_tax=0,
        )
        # operating_income = 5000
        # ordinary_income = 5000
        # income_before_tax = 5000 + 500 - 1000 = 4500
        assert is_.income_before_tax == 4_500

    def test_negative_net_income(self):
        is_ = IncomeStatement(
            revenue=1_000,
            cost_of_goods_sold=2_000,  # 原価が売上を超える赤字
            income_tax=0,
        )
        assert is_.net_income == -1_000


class TestBalanceSheet:
    def test_auto_calculation(self):
        bs = BalanceSheet(
            cash_and_equivalents=1_000,
            accounts_receivable=2_000,
            inventory=500,
            other_current_assets=500,
            property_plant_equipment=5_000,
            intangible_assets=1_000,
            investments=500,
            accounts_payable=1_000,
            short_term_debt=500,
            other_current_liabilities=500,
            long_term_debt=3_000,
            other_non_current_liabilities=500,
            common_stock=3_000,
            retained_earnings=3_000,
        )
        assert bs.total_current_assets == 4_000
        assert bs.total_non_current_assets == 6_500
        assert bs.total_assets == 10_500
        assert bs.total_current_liabilities == 2_000
        assert bs.total_non_current_liabilities == 3_500
        assert bs.total_liabilities == 5_500
        assert bs.total_equity == 6_000


class TestCashFlowStatement:
    def test_auto_calculation(self):
        cf = CashFlowStatement(
            net_income=1_000,
            depreciation_amortization=500,
            changes_in_working_capital=-200,
            capital_expenditures=-800,
            debt_issuance=1_000,
            debt_repayment=-500,
            dividends_paid=-300,
        )
        assert cf.operating_cash_flow == 1_300   # 1000 + 500 - 200
        assert cf.investing_cash_flow == -800
        assert cf.financing_cash_flow == 200      # 1000 - 500 - 300
        assert cf.net_change_in_cash == 700       # 1300 - 800 + 200
