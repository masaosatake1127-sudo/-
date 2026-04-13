# 分析エンジン・レポート生成 (`analyzer.py` / `report.py`)

---

## FinancialAnalyzer（分析エンジン）

`financial_analysis/analyzer.py`

### 概要

`FinancialRatios` で計算した各指標に対して、評価コメントと総合スコア（0〜100）を付与します。

### 使い方

```python
from financial_analysis import FinancialAnalyzer

analyzer = FinancialAnalyzer()
result = analyzer.analyze(data)   # FinancialData を渡す

print(result.overall_score)       # 例: 73.5
print(result.overall_comments)    # ['財務状況は概ね健全です...']
```

### AnalysisResult（結果オブジェクト）

```python
@dataclass
class AnalysisResult:
    company_name: str
    period: str

    profitability: ProfitabilityRatios
    safety: SafetyRatios
    efficiency: EfficiencyRatios
    growth: GrowthRatios
    cash_flow: CashFlowRatios

    profitability_comments: List[str]
    safety_comments: List[str]
    efficiency_comments: List[str]
    growth_comments: List[str]
    cash_flow_comments: List[str]

    overall_score: Optional[float]   # 0〜100
    overall_comments: List[str]
```

### 総合スコア配点

| カテゴリ | 満点 | 主な基準 |
|----------|------|---------|
| 収益性 | 30点 | 営業利益率: ≥15%→30点, ≥5%→20点, ≥0%→10点 |
| 安全性 | 30点 | 自己資本比率(15点) + 流動比率(15点) |
| 効率性 | 20点 | 総資産回転率: ≥1.5→20点, ≥0.8→13点 |
| CF | 20点 | FCF≥0 かつ CFマージン≥10%→20点 |
| **合計** | **100点** | |

### 評価コメントの閾値

**収益性**
- 売上総利益率: ≥50% 非常に高い / ≥30% 良好 / ≥10% 標準 / <10% 改善必要
- 営業利益率: ≥15% 優秀 / ≥5% 安定 / ≥0% 要改善 / <0% 損失
- ROE: ≥15% 高効率 / ≥8% 標準 / <8% 要改善

**安全性**
- 流動比率: ≥200% 十分 / ≥100% 概ね問題なし / <100% リスクあり
- 自己資本比率: ≥50% 非常に健全 / ≥30% 健全 / ≥15% 高レバレッジ / <15% 強化急務
- ICレシオ: ≥5倍 十分 / ≥2倍 余裕少 / <2倍 懸念

**効率性**
- 総資産回転率: ≥1.5回 効率的 / ≥0.8回 標準 / <0.8回 改善余地
- 売掛金回収日数: ≤30日 迅速 / ≤60日 標準 / >60日 要改善

**成長性**
- 売上高成長率: ≥20% 高成長 / ≥5% 安定増収 / ≥0% 横ばい / <0% 減収

**CF**
- CFマージン: ≥15% 優秀 / ≥5% 安定 / <5% 要改善
- FCF: ≥0 自己資金調達可 / <0 要管理

---

## ReportGenerator（レポート生成）

`financial_analysis/report.py`

### 使い方

```python
from financial_analysis import ReportGenerator

generator = ReportGenerator()

# プレーンテキスト
text_report = generator.generate_text(result)

# Markdown
md_report = generator.generate_markdown(result)

# ファイル保存
with open("report.md", "w", encoding="utf-8") as f:
    f.write(md_report)
```

### テキストレポートの構成

```
============================================================
  財務分析レポート: 株式会社〇〇
  対象期間: 2024年3月期
============================================================

総合評価スコア: 73.5 / 100
  → 財務状況は概ね健全です...

----------------------------------------
【収益性指標】
  売上総利益率:    60.00 %
  営業利益率:      18.00 %
  ...

【安全性指標】
【効率性指標】
【成長性指標】
【キャッシュフロー指標】
```

### Markdownレポートの構成

```markdown
# 財務分析レポート: 株式会社〇〇
**対象期間:** 2024年3月期

## 総合評価スコア: 73.5 / 100
> 財務状況は概ね健全です...

## 収益性指標
| 指標 | 値 |
|------|-----|
| 売上総利益率 | 60.00% |
...

## 安全性指標
## 効率性指標
## 成長性指標
## キャッシュフロー指標
```
