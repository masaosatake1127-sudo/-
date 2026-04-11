"""
サンプル財務データ

架空の企業「株式会社サンプルテック」の財務諸表サンプルデータです。
"""

from financial_analysis.models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialData,
)

# ======================================================
# 当期 (2024年3月期)
# ======================================================

income_stmt_current = IncomeStatement(
    period="2024年3月期",
    revenue=50_000_000,              # 売上高: 5,000万円
    cost_of_goods_sold=20_000_000,   # 売上原価: 2,000万円
    selling_expenses=8_000_000,      # 販売費: 800万円
    general_admin_expenses=4_000_000,  # 一般管理費: 400万円
    non_operating_income=300_000,    # 営業外収益: 30万円
    non_operating_expenses=500_000,  # 営業外費用(支払利息): 50万円
    extraordinary_income=0,
    extraordinary_losses=200_000,    # 特別損失: 20万円
    income_tax=2_700_000,            # 法人税等: 270万円
)

balance_sheet_current = BalanceSheet(
    period="2024年3月期",
    # 流動資産
    cash_and_equivalents=5_000_000,   # 現金: 500万円
    accounts_receivable=8_000_000,    # 売掛金: 800万円
    inventory=3_000_000,              # 棚卸資産: 300万円
    other_current_assets=1_000_000,   # その他流動資産: 100万円
    # 固定資産
    property_plant_equipment=15_000_000,  # 有形固定資産: 1,500万円
    intangible_assets=2_000_000,          # 無形固定資産: 200万円
    investments=3_000_000,                # 投資: 300万円
    # 流動負債
    accounts_payable=4_000_000,       # 買掛金: 400万円
    short_term_debt=3_000_000,        # 短期借入金: 300万円
    other_current_liabilities=2_000_000,  # その他流動負債: 200万円
    # 固定負債
    long_term_debt=8_000_000,         # 長期借入金: 800万円
    other_non_current_liabilities=1_000_000,
    # 純資産
    common_stock=10_000_000,          # 資本金: 1,000万円
    retained_earnings=9_000_000,      # 利益剰余金: 900万円
    other_equity=0,
)

cash_flow_current = CashFlowStatement(
    period="2024年3月期",
    net_income=income_stmt_current.net_income,
    depreciation_amortization=2_000_000,   # 減価償却費: 200万円
    changes_in_working_capital=-500_000,   # 運転資本変動: -50万円
    other_operating_cf=300_000,
    capital_expenditures=-3_000_000,       # 設備投資: -300万円
    acquisitions=0,
    other_investing_cf=0,
    debt_issuance=2_000_000,               # 借入増加
    debt_repayment=-1_500_000,             # 借入返済
    dividends_paid=-1_000_000,             # 配当: -100万円
    other_financing_cf=0,
)

# ======================================================
# 前期 (2023年3月期)
# ======================================================

income_stmt_previous = IncomeStatement(
    period="2023年3月期",
    revenue=44_000_000,              # 売上高: 4,400万円
    cost_of_goods_sold=18_500_000,
    selling_expenses=7_200_000,
    general_admin_expenses=3_800_000,
    non_operating_income=200_000,
    non_operating_expenses=600_000,
    extraordinary_income=0,
    extraordinary_losses=0,
    income_tax=2_200_000,
)

balance_sheet_previous = BalanceSheet(
    period="2023年3月期",
    cash_and_equivalents=4_200_000,
    accounts_receivable=7_000_000,
    inventory=2_800_000,
    other_current_assets=800_000,
    property_plant_equipment=14_000_000,
    intangible_assets=1_500_000,
    investments=2_500_000,
    accounts_payable=3_500_000,
    short_term_debt=2_500_000,
    other_current_liabilities=1_800_000,
    long_term_debt=9_000_000,
    other_non_current_liabilities=900_000,
    common_stock=10_000_000,
    retained_earnings=7_600_000,
    other_equity=0,
)

# ======================================================
# FinancialData オブジェクト
# ======================================================

sample_financial_data = FinancialData(
    company_name="株式会社サンプルテック",
    income_statement=income_stmt_current,
    balance_sheet=balance_sheet_current,
    cash_flow_statement=cash_flow_current,
    previous_income_statement=income_stmt_previous,
    previous_balance_sheet=balance_sheet_previous,
)
