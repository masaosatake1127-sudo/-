# データモデル (`financial_analysis/models.py`)

財務諸表の数値を保持するデータクラス群です。  
`__post_init__` により、省略したフィールドは自動計算されます。

---

## IncomeStatement（損益計算書）

```python
@dataclass
class IncomeStatement:
    revenue: float                  # 売上高（必須）
    cost_of_goods_sold: float       # 売上原価（必須）
    gross_profit: Optional[float]   # 売上総利益（自動: revenue - COGS）

    selling_expenses: float = 0.0
    general_admin_expenses: float = 0.0
    operating_expenses: Optional[float]  # 自動: 販売費 + 一般管理費

    operating_income: Optional[float]    # 自動: 粗利 - 営業費用
    non_operating_income: float = 0.0
    non_operating_expenses: float = 0.0
    ordinary_income: Optional[float]     # 自動: 営業利益 ± 営業外損益

    extraordinary_income: float = 0.0
    extraordinary_losses: float = 0.0
    income_before_tax: Optional[float]   # 自動: 経常利益 ± 特別損益

    income_tax: float = 0.0
    net_income: Optional[float]          # 自動: 税引前利益 - 法人税等

    period: str = ""                     # 例: "2024年3月期"
```

### 自動計算の流れ

```
売上高 - 売上原価 = 売上総利益
売上総利益 - 営業費用 = 営業利益
営業利益 ± 営業外損益 = 経常利益
経常利益 ± 特別損益 = 税引前当期純利益
税引前当期純利益 - 法人税等 = 当期純利益
```

---

## BalanceSheet（貸借対照表）

```python
@dataclass
class BalanceSheet:
    # 流動資産
    cash_and_equivalents: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    other_current_assets: float = 0.0
    total_current_assets: Optional[float]       # 自動計算

    # 固定資産
    property_plant_equipment: float = 0.0
    intangible_assets: float = 0.0
    investments: float = 0.0
    total_non_current_assets: Optional[float]   # 自動計算
    total_assets: Optional[float]               # 自動計算

    # 流動負債
    accounts_payable: float = 0.0
    short_term_debt: float = 0.0
    other_current_liabilities: float = 0.0
    total_current_liabilities: Optional[float]  # 自動計算

    # 固定負債
    long_term_debt: float = 0.0
    other_non_current_liabilities: float = 0.0
    total_non_current_liabilities: Optional[float]  # 自動計算
    total_liabilities: Optional[float]          # 自動計算

    # 純資産
    common_stock: float = 0.0
    retained_earnings: float = 0.0
    other_equity: float = 0.0
    total_equity: Optional[float]               # 自動計算

    period: str = ""
```

---

## CashFlowStatement（キャッシュフロー計算書）

```python
@dataclass
class CashFlowStatement:
    # 営業CF
    net_income: float = 0.0
    depreciation_amortization: float = 0.0
    changes_in_working_capital: float = 0.0
    other_operating_cf: float = 0.0
    operating_cash_flow: Optional[float]   # 自動計算

    # 投資CF
    capital_expenditures: float = 0.0     # 設備投資（マイナス値）
    acquisitions: float = 0.0
    other_investing_cf: float = 0.0
    investing_cash_flow: Optional[float]  # 自動計算

    # 財務CF
    debt_issuance: float = 0.0
    debt_repayment: float = 0.0           # 返済（マイナス値）
    dividends_paid: float = 0.0           # 配当（マイナス値）
    other_financing_cf: float = 0.0
    financing_cash_flow: Optional[float]  # 自動計算

    net_change_in_cash: Optional[float]   # 自動: 三CF合計

    period: str = ""
```

---

## FinancialData（まとめコンテナ）

```python
@dataclass
class FinancialData:
    company_name: str
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement
    previous_income_statement: Optional[IncomeStatement] = None  # 前期（成長率算出に使用）
    previous_balance_sheet: Optional[BalanceSheet] = None
```

---

## 使用例

```python
from financial_analysis.models import IncomeStatement, BalanceSheet, CashFlowStatement, FinancialData

is_ = IncomeStatement(
    period="2024年3月期",
    revenue=50_000_000,
    cost_of_goods_sold=20_000_000,
    selling_expenses=8_000_000,
    general_admin_expenses=4_000_000,
    income_tax=2_700_000,
)
# gross_profit, operating_income, net_income は自動計算される

bs = BalanceSheet(
    cash_and_equivalents=5_000_000,
    accounts_receivable=8_000_000,
    # ... 省略時は0
)

cf = CashFlowStatement(
    net_income=is_.net_income,
    depreciation_amortization=2_000_000,
    capital_expenditures=-3_000_000,
)

data = FinancialData(
    company_name="株式会社〇〇",
    income_statement=is_,
    balance_sheet=bs,
    cash_flow_statement=cf,
)
```
