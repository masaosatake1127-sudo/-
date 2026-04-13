# アーキテクチャ概要

---

## ディレクトリ構成

```
プロジェクトルート/
├── financial_analysis/          # コアライブラリ
│   ├── __init__.py              # 公開API定義
│   ├── models.py                # データモデル（dataclass）
│   ├── ratios.py                # 財務比率計算
│   ├── analyzer.py              # 評価・スコアリング
│   ├── report.py                # レポート生成（テキスト / Markdown）
│   ├── file_loader.py           # 統合ローダー（拡張子判定）
│   ├── pdf_loader.py            # PDFローダー（PyMuPDF）
│   ├── excel_loader.py          # Excelローダー（openpyxl）
│   ├── word_loader.py           # Wordローダー（python-docx）
│   └── google_drive_loader.py   # Google Drive ローダー
│
├── examples/
│   ├── run_analysis.py          # CLIスクリプト
│   ├── sample_data.py           # サンプル財務データ
│   ├── test_income_statement.pdf
│   ├── test_monthly_pl.xlsx
│   └── test_monthly_pl.docx
│
├── tests/
│   ├── test_models.py
│   ├── test_ratios.py
│   └── test_analyzer.py
│
├── docs/                        # ドキュメント（このフォルダ）
│
├── app.py                       # Streamlit Web UI
├── financial_analysis_colab.ipynb  # Google Colab ノートブック
└── requirements.txt
```

---

## データフロー

```
ファイル（PDF/Excel/Word/Google Drive）
        │
        ▼
  load_financial_data()          ← file_loader.py（拡張子で振り分け）
        │
        ├── PdfIncomeStatementLoader      (PyMuPDF)
        ├── ExcelIncomeStatementLoader    (openpyxl)
        ├── WordIncomeStatementLoader     (python-docx)
        └── GoogleDriveLoader             (requests / google-api)
        │
        ▼
  FinancialData                  ← models.py
    ├── IncomeStatement
    ├── BalanceSheet
    ├── CashFlowStatement
    └── (前期データ)
        │
        ▼
  FinancialRatios                ← ratios.py
    ├── profitability()
    ├── safety()
    ├── efficiency()
    ├── growth()
    └── cash_flow_ratios()
        │
        ▼
  FinancialAnalyzer.analyze()    ← analyzer.py
    → AnalysisResult
      ├── 各指標値
      ├── 評価コメント
      └── 総合スコア (0〜100)
        │
        ▼
  ReportGenerator                ← report.py
    ├── generate_text()          → .txt
    └── generate_markdown()      → .md
```

---

## 依存ライブラリ

| ライブラリ | 用途 | バージョン |
|-----------|------|-----------|
| `pymupdf` | PDF テキスト・座標抽出 | ≥1.23 |
| `openpyxl` | Excel (.xlsx) 読み込み | ≥3.1 |
| `python-docx` | Word (.docx) 読み込み | ≥1.0 |
| `requests` | Google Drive 公開ファイルDL | ≥2.31 |
| `google-api-python-client` | Google Drive API（サービスアカウント） | ≥2.0 |
| `google-auth` | Google 認証 | ≥2.0 |
| `streamlit` | Web UI | ≥1.30 |
| `pytest` | テスト実行 | ≥7.0 |

---

## 公開API（`financial_analysis/__init__.py`）

```python
from financial_analysis import (
    # データモデル
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialData,

    # 比率計算
    FinancialRatios,

    # 分析・レポート
    FinancialAnalyzer,
    ReportGenerator,

    # ローダー
    PdfIncomeStatementLoader,
    ExcelIncomeStatementLoader,
    WordIncomeStatementLoader,
    GoogleDriveLoader,

    # ユーティリティ
    load_financial_data,
    extract_debug_text,
)
```

---

## テスト

```bash
# 全テスト実行
pytest tests/ -v

# 個別ファイル
pytest tests/test_models.py -v
pytest tests/test_ratios.py -v
pytest tests/test_analyzer.py -v
```

テストファイル一覧:

| ファイル | 内容 |
|---------|------|
| `test_models.py` | dataclassの自動計算ロジック |
| `test_ratios.py` | 財務比率の計算精度 |
| `test_analyzer.py` | 評価コメント・スコアのロジック |
