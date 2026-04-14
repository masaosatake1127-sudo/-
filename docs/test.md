# テスト仕様・実行方法

---

## テスト実行

### 全テスト実行

```bash
pytest tests/ -v
```

### 個別ファイル実行

```bash
pytest tests/test_models.py -v     # データモデル
pytest tests/test_ratios.py -v     # 財務比率
pytest tests/test_analyzer.py -v   # 分析エンジン・レポート
```

### オプション

```bash
# 失敗したテストだけ再実行
pytest tests/ --lf

# カバレッジを表示（pytest-cov が必要）
pytest tests/ --cov=financial_analysis

# キャッシュをクリアして実行
pytest tests/ --cache-clear
```

---

## テストファイル一覧

### `tests/test_models.py` — データモデルのテスト（8件）

| テストクラス | テスト名 | 検証内容 |
|-------------|---------|---------|
| `TestIncomeStatement` | `test_auto_calculation` | 粗利・営業利益・純利益の自動計算 |
| | `test_non_operating_items` | 営業外収益・費用の反映 |
| | `test_extraordinary_items` | 特別利益・損失の反映 |
| | `test_negative_net_income` | 赤字（純損失）の計算 |
| `TestBalanceSheet` | `test_auto_calculation` | 流動資産・固定資産・負債・純資産合計の自動計算 |
| `TestCashFlowStatement` | `test_auto_calculation` | 営業CF・投資CF・財務CF・純増減の自動計算 |

#### 主要な検証値

```python
# IncomeStatement 自動計算
revenue=10_000, cost_of_goods_sold=6_000
→ gross_profit = 4_000
→ operating_income = 2_500  (selling=1000, admin=500)
→ net_income = 2_000         (tax=500)

# 赤字ケース
revenue=1_000, cost_of_goods_sold=2_000
→ net_income = -1_000
```

---

### `tests/test_ratios.py` — 財務比率計算のテスト（9件）

#### ベースデータ

```
売上高:    100,000
売上原価:   40,000
販管費:     20,000
営業利益:   40,000
純利益:     30,000
総資産:     85,000
純資産:     47,000
流動資産:   45,000
流動負債:   15,000
```

| テストクラス | テスト名 | 期待値 |
|-------------|---------|--------|
| `TestProfitabilityRatios` | `test_gross_profit_margin` | 60.0% |
| | `test_operating_profit_margin` | 40.0% |
| | `test_roe_calculation` | 63.83%（30000/47000×100） |
| `TestSafetyRatios` | `test_current_ratio` | 300.0%（45000/15000×100） |
| | `test_equity_ratio` | 55.29%（47000/85000×100） |
| | `test_interest_coverage` | 20.0倍（40000/2000） |
| `TestEfficiencyRatios` | `test_asset_turnover` | 1.176回（100000/85000） |
| | `test_inventory_turnover` | 4.0回（40000/10000） |
| | `test_days_sales_outstanding` | 73.0日（365/(100000/20000)） |
| `TestGrowthRatios` | `test_no_previous_data` | None（前期データなし） |
| | `test_growth_with_previous_data` | 25.0%（(100000-80000)/80000×100） |
| `TestCashFlowRatios` | `test_free_cash_flow` | 26,000（34000-8000） |
| | `test_zero_revenue_safe` | ゼロ除算が発生しないこと |

---

### `tests/test_analyzer.py` — 分析エンジン・レポートのテスト（8件）

| テストクラス | テスト名 | 検証内容 |
|-------------|---------|---------|
| `TestFinancialAnalyzer` | `test_returns_analysis_result` | 企業名・期間がセットされること |
| | `test_overall_score_range` | スコアが 0〜100 の範囲内 |
| | `test_comments_not_empty` | 各コメントが1件以上生成されること |
| | `test_growth_without_previous` | 前期データなし → growth_rate が None |
| `TestReportGenerator` | `test_text_report_contains_company_name` | 企業名がレポートに含まれること |
| | `test_text_report_contains_sections` | 5つのセクション見出しが存在すること |
| | `test_markdown_report_has_headers` | `#` 見出しが存在すること |
| | `test_markdown_report_has_table` | Markdownテーブルが存在すること |

---

## テスト追加の方針

新機能を追加した場合は以下の観点でテストを追加してください。

### データモデル (`test_models.py`)
- フィールドの自動計算が正しいか
- エッジケース（0・負値・None）で例外が発生しないか

### 財務比率 (`test_ratios.py`)
- 計算式の数値精度（`abs(actual - expected) < 0.01`）
- ゼロ除算が発生しないか（売上高=0、総資産=0 等）
- `None` が返るべきケースで `None` が返るか

### 分析・レポート (`test_analyzer.py`)
- 分析結果の型・範囲が正しいか
- レポート文字列に必要なセクションが含まれるか

---

## CI への組み込み（今後）

現在はローカル実行のみ。GitHub Actions 等で自動化する場合の設定例:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```
