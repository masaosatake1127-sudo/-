"""
財務諸表データモデル

損益計算書・貸借対照表・キャッシュフロー計算書のデータ構造を定義します。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IncomeStatement:
    """損益計算書 (P&L Statement)"""

    # 収益
    revenue: float                          # 売上高
    cost_of_goods_sold: float               # 売上原価
    gross_profit: Optional[float] = None   # 売上総利益（自動計算可）

    # 費用
    selling_expenses: float = 0.0          # 販売費
    general_admin_expenses: float = 0.0    # 一般管理費
    operating_expenses: Optional[float] = None  # 営業費用合計（自動計算可）

    # 利益
    operating_income: Optional[float] = None    # 営業利益（自動計算可）
    non_operating_income: float = 0.0           # 営業外収益
    non_operating_expenses: float = 0.0         # 営業外費用
    ordinary_income: Optional[float] = None     # 経常利益（自動計算可）

    extraordinary_income: float = 0.0           # 特別利益
    extraordinary_losses: float = 0.0           # 特別損失
    income_before_tax: Optional[float] = None   # 税引前当期純利益（自動計算可）

    income_tax: float = 0.0                     # 法人税等
    net_income: Optional[float] = None          # 当期純利益（自動計算可）

    period: str = ""                            # 会計期間（例: "2024年3月期"）

    def __post_init__(self):
        """自動計算フィールドを補完する"""
        if self.gross_profit is None:
            self.gross_profit = self.revenue - self.cost_of_goods_sold

        if self.operating_expenses is None:
            self.operating_expenses = self.selling_expenses + self.general_admin_expenses

        if self.operating_income is None:
            self.operating_income = self.gross_profit - self.operating_expenses

        if self.ordinary_income is None:
            self.ordinary_income = (
                self.operating_income
                + self.non_operating_income
                - self.non_operating_expenses
            )

        if self.income_before_tax is None:
            self.income_before_tax = (
                self.ordinary_income
                + self.extraordinary_income
                - self.extraordinary_losses
            )

        if self.net_income is None:
            self.net_income = self.income_before_tax - self.income_tax


@dataclass
class BalanceSheet:
    """貸借対照表 (Balance Sheet)"""

    # 流動資産
    cash_and_equivalents: float = 0.0           # 現金及び現金同等物
    accounts_receivable: float = 0.0            # 売掛金
    inventory: float = 0.0                      # 棚卸資産
    other_current_assets: float = 0.0           # その他の流動資産
    total_current_assets: Optional[float] = None  # 流動資産合計（自動計算可）

    # 固定資産
    property_plant_equipment: float = 0.0       # 有形固定資産
    intangible_assets: float = 0.0              # 無形固定資産
    investments: float = 0.0                    # 投資その他の資産
    total_non_current_assets: Optional[float] = None  # 固定資産合計（自動計算可）

    total_assets: Optional[float] = None        # 資産合計（自動計算可）

    # 流動負債
    accounts_payable: float = 0.0               # 買掛金
    short_term_debt: float = 0.0                # 短期借入金
    other_current_liabilities: float = 0.0      # その他の流動負債
    total_current_liabilities: Optional[float] = None  # 流動負債合計（自動計算可）

    # 固定負債
    long_term_debt: float = 0.0                 # 長期借入金
    other_non_current_liabilities: float = 0.0  # その他の固定負債
    total_non_current_liabilities: Optional[float] = None  # 固定負債合計（自動計算可）

    total_liabilities: Optional[float] = None   # 負債合計（自動計算可）

    # 純資産
    common_stock: float = 0.0                   # 資本金
    retained_earnings: float = 0.0             # 利益剰余金
    other_equity: float = 0.0                  # その他の純資産
    total_equity: Optional[float] = None        # 純資産合計（自動計算可）

    period: str = ""                            # 会計期間

    def __post_init__(self):
        """自動計算フィールドを補完する"""
        if self.total_current_assets is None:
            self.total_current_assets = (
                self.cash_and_equivalents
                + self.accounts_receivable
                + self.inventory
                + self.other_current_assets
            )

        if self.total_non_current_assets is None:
            self.total_non_current_assets = (
                self.property_plant_equipment
                + self.intangible_assets
                + self.investments
            )

        if self.total_assets is None:
            self.total_assets = self.total_current_assets + self.total_non_current_assets

        if self.total_current_liabilities is None:
            self.total_current_liabilities = (
                self.accounts_payable
                + self.short_term_debt
                + self.other_current_liabilities
            )

        if self.total_non_current_liabilities is None:
            self.total_non_current_liabilities = (
                self.long_term_debt + self.other_non_current_liabilities
            )

        if self.total_liabilities is None:
            self.total_liabilities = (
                self.total_current_liabilities + self.total_non_current_liabilities
            )

        if self.total_equity is None:
            self.total_equity = (
                self.common_stock + self.retained_earnings + self.other_equity
            )


@dataclass
class CashFlowStatement:
    """キャッシュフロー計算書 (Cash Flow Statement)"""

    # 営業活動によるキャッシュフロー
    net_income: float = 0.0                     # 当期純利益
    depreciation_amortization: float = 0.0      # 減価償却費
    changes_in_working_capital: float = 0.0     # 運転資本の変動
    other_operating_cf: float = 0.0             # その他の営業CF
    operating_cash_flow: Optional[float] = None  # 営業CF合計（自動計算可）

    # 投資活動によるキャッシュフロー
    capital_expenditures: float = 0.0           # 設備投資（マイナス値）
    acquisitions: float = 0.0                   # 買収（マイナス値）
    other_investing_cf: float = 0.0             # その他の投資CF
    investing_cash_flow: Optional[float] = None  # 投資CF合計（自動計算可）

    # 財務活動によるキャッシュフロー
    debt_issuance: float = 0.0                  # 借入金の増加
    debt_repayment: float = 0.0                 # 借入金の返済（マイナス値）
    dividends_paid: float = 0.0                 # 配当金支払い（マイナス値）
    other_financing_cf: float = 0.0             # その他の財務CF
    financing_cash_flow: Optional[float] = None  # 財務CF合計（自動計算可）

    net_change_in_cash: Optional[float] = None  # 現金の純増減（自動計算可）

    period: str = ""                            # 会計期間

    def __post_init__(self):
        """自動計算フィールドを補完する"""
        if self.operating_cash_flow is None:
            self.operating_cash_flow = (
                self.net_income
                + self.depreciation_amortization
                + self.changes_in_working_capital
                + self.other_operating_cf
            )

        if self.investing_cash_flow is None:
            self.investing_cash_flow = (
                self.capital_expenditures
                + self.acquisitions
                + self.other_investing_cf
            )

        if self.financing_cash_flow is None:
            self.financing_cash_flow = (
                self.debt_issuance
                + self.debt_repayment
                + self.dividends_paid
                + self.other_financing_cf
            )

        if self.net_change_in_cash is None:
            self.net_change_in_cash = (
                self.operating_cash_flow
                + self.investing_cash_flow
                + self.financing_cash_flow
            )


@dataclass
class FinancialData:
    """企業の財務データをまとめたコンテナ"""

    company_name: str
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement
    previous_income_statement: Optional[IncomeStatement] = None
    previous_balance_sheet: Optional[BalanceSheet] = None
