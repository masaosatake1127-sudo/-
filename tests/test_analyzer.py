"""
財務分析エンジンのテスト
"""

import pytest
from financial_analysis.models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialData,
)
from financial_analysis.analyzer import FinancialAnalyzer
from financial_analysis.report import ReportGenerator


def make_financial_data(company_name="テスト株式会社"):
    is_ = IncomeStatement(
        period="2024年3月期",
        revenue=50_000_000,
        cost_of_goods_sold=20_000_000,
        selling_expenses=8_000_000,
        general_admin_expenses=4_000_000,
        non_operating_expenses=500_000,
        income_tax=2_700_000,
    )
    bs = BalanceSheet(
        period="2024年3月期",
        cash_and_equivalents=5_000_000,
        accounts_receivable=8_000_000,
        inventory=3_000_000,
        other_current_assets=1_000_000,
        property_plant_equipment=15_000_000,
        intangible_assets=2_000_000,
        investments=3_000_000,
        accounts_payable=4_000_000,
        short_term_debt=3_000_000,
        other_current_liabilities=2_000_000,
        long_term_debt=8_000_000,
        other_non_current_liabilities=1_000_000,
        common_stock=10_000_000,
        retained_earnings=9_000_000,
    )
    cf = CashFlowStatement(
        period="2024年3月期",
        net_income=is_.net_income,
        depreciation_amortization=2_000_000,
        changes_in_working_capital=-500_000,
        capital_expenditures=-3_000_000,
        debt_issuance=2_000_000,
        debt_repayment=-1_500_000,
        dividends_paid=-1_000_000,
    )
    return FinancialData(
        company_name=company_name,
        income_statement=is_,
        balance_sheet=bs,
        cash_flow_statement=cf,
    )


class TestFinancialAnalyzer:
    def test_returns_analysis_result(self):
        data = make_financial_data()
        analyzer = FinancialAnalyzer()
        result = analyzer.analyze(data)
        assert result.company_name == "テスト株式会社"
        assert result.period == "2024年3月期"

    def test_overall_score_range(self):
        data = make_financial_data()
        analyzer = FinancialAnalyzer()
        result = analyzer.analyze(data)
        assert 0 <= result.overall_score <= 100

    def test_comments_not_empty(self):
        data = make_financial_data()
        analyzer = FinancialAnalyzer()
        result = analyzer.analyze(data)
        assert len(result.profitability_comments) > 0
        assert len(result.safety_comments) > 0
        assert len(result.overall_comments) > 0

    def test_growth_without_previous(self):
        data = make_financial_data()
        analyzer = FinancialAnalyzer()
        result = analyzer.analyze(data)
        assert result.growth.revenue_growth_rate is None


class TestReportGenerator:
    def setup_method(self):
        data = make_financial_data()
        analyzer = FinancialAnalyzer()
        self.result = analyzer.analyze(data)
        self.generator = ReportGenerator()

    def test_text_report_contains_company_name(self):
        report = self.generator.generate_text(self.result)
        assert "テスト株式会社" in report

    def test_text_report_contains_sections(self):
        report = self.generator.generate_text(self.result)
        assert "収益性指標" in report
        assert "安全性指標" in report
        assert "効率性指標" in report
        assert "成長性指標" in report
        assert "キャッシュフロー指標" in report

    def test_markdown_report_has_headers(self):
        report = self.generator.generate_markdown(self.result)
        assert "# 財務分析レポート" in report
        assert "## 収益性指標" in report
        assert "## 安全性指標" in report

    def test_markdown_report_has_table(self):
        report = self.generator.generate_markdown(self.result)
        assert "|------|" in report
