# 財務比率 (`financial_analysis/ratios.py`)

`FinancialRatios` クラスが財務諸表データから各種指標を計算します。

---

## 計算クラス

```python
ratios = FinancialRatios(
    income_stmt,
    balance_sheet,
    cash_flow,
    prev_income_stmt=None,   # 前期（成長率算出に使用）
    prev_balance_sheet=None,
)
```

---

## 収益性指標 — `ProfitabilityRatios`

| メソッド | 指標 | 計算式 |
|----------|------|--------|
| `gross_profit_margin` | 売上総利益率 (%) | 売上総利益 / 売上高 × 100 |
| `operating_profit_margin` | 営業利益率 (%) | 営業利益 / 売上高 × 100 |
| `net_profit_margin` | 純利益率 (%) | 当期純利益 / 売上高 × 100 |
| `return_on_assets` | ROA (%) | 当期純利益 / 総資産 × 100 |
| `return_on_equity` | ROE (%) | 当期純利益 / 純資産 × 100 |
| `ebitda_margin` | EBITDAマージン (%) | (営業利益 + 減価償却費) / 売上高 × 100 |

```python
p = ratios.profitability()
print(p.operating_profit_margin)  # 例: 12.5
```

---

## 安全性指標 — `SafetyRatios`

| メソッド | 指標 | 計算式 |
|----------|------|--------|
| `current_ratio` | 流動比率 (%) | 流動資産 / 流動負債 × 100 |
| `quick_ratio` | 当座比率 (%) | (現金 + 売掛金) / 流動負債 × 100 |
| `debt_to_equity_ratio` | 負債資本比率 (倍) | 負債合計 / 純資産合計 |
| `equity_ratio` | 自己資本比率 (%) | 純資産 / 総資産 × 100 |
| `interest_coverage_ratio` | ICレシオ (倍) | 営業利益 / 営業外費用（支払利息がある場合のみ）|

```python
s = ratios.safety()
print(s.equity_ratio)            # 例: 42.1
print(s.interest_coverage_ratio) # 例: 7.3 または None
```

---

## 効率性指標 — `EfficiencyRatios`

| メソッド | 指標 | 計算式 |
|----------|------|--------|
| `asset_turnover` | 総資産回転率 (回) | 売上高 / 総資産 |
| `inventory_turnover` | 棚卸資産回転率 (回) | 売上原価 / 棚卸資産（棚卸資産>0の場合） |
| `receivables_turnover` | 売掛金回転率 (回) | 売上高 / 売掛金（売掛金>0の場合） |
| `days_sales_outstanding` | 売掛金回収日数 (日) | 365 / 売掛金回転率 |
| `days_inventory_outstanding` | 棚卸資産回転日数 (日) | 365 / 棚卸資産回転率 |

---

## 成長性指標 — `GrowthRatios`

> 前期データ（`prev_income_stmt` / `prev_balance_sheet`）がない場合はすべて `None`

| メソッド | 指標 | 計算式 |
|----------|------|--------|
| `revenue_growth_rate` | 売上高成長率 (%) | (当期 - 前期) / |前期| × 100 |
| `operating_income_growth_rate` | 営業利益成長率 (%) | 同上 |
| `net_income_growth_rate` | 純利益成長率 (%) | 同上 |
| `total_assets_growth_rate` | 総資産成長率 (%) | 同上 |

---

## キャッシュフロー指標 — `CashFlowRatios`

| メソッド | 指標 | 計算式 |
|----------|------|--------|
| `operating_cf_margin` | 営業CFマージン (%) | 営業CF / 売上高 × 100 |
| `free_cash_flow` | フリーキャッシュフロー (円) | 営業CF + 設備投資（capexは負値） |
| `cash_flow_to_debt` | CF / 有利子負債 (倍) | 営業CF / (短期+長期借入金)（借入がある場合のみ） |

---

## ユーティリティメソッド

```python
# ゼロ除算防止: 分母=0 のとき None を返す
FinancialRatios._safe_divide(numerator, denominator) -> Optional[float]

# Optional[float] を % 換算 (None は 0.0 扱い)
FinancialRatios._pct(value) -> float
```

---

## 使用例

```python
from financial_analysis.ratios import FinancialRatios

ratios = FinancialRatios(
    income_stmt=data.income_statement,
    balance_sheet=data.balance_sheet,
    cash_flow=data.cash_flow_statement,
    prev_income_stmt=data.previous_income_statement,
)

p = ratios.profitability()
s = ratios.safety()
e = ratios.efficiency()
g = ratios.growth()
cf = ratios.cash_flow_ratios()
```
