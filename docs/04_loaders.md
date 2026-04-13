# ファイルローダー群

対応形式: **PDF** / **Excel (.xlsx .xls .xlsm)** / **Word (.docx)** / **Google Drive**

---

## 統合ローダー — `load_financial_data`

`financial_analysis/file_loader.py`

拡張子を自動判定し、適切なローダーに振り分けます。

```python
from financial_analysis import load_financial_data

data = load_financial_data(
    file_path,                # 必須: ファイルパス
    company_name="株式会社〇〇",   # 省略時: ファイル名
    period="2024年3月期",          # 省略時: ""
    unit=1.0,                      # 単位倍率（千円=1000, 百万円=1000000）
    sheet_name=None,               # Excelのシート名（省略時: 自動選択）
)
```

### デバッグ確認

```python
from financial_analysis import extract_debug_text

# 生テキスト・表構造を文字列で取得
debug_str = extract_debug_text("決算書.pdf")
print(debug_str)
```

---

## PDFローダー

`financial_analysis/pdf_loader.py` — PyMuPDF (fitz) を使用

### 数値認識

- 通常数値: `1,234,567`
- △▲ 表記の負数: `△500` → `-500`
- カッコ表記の負数: `(500)` → `-500`

### テーブル解析パターン

| パターン | 形式 | 説明 |
|----------|------|------|
| A | 科目が行・月が列 | 合計列を優先使用 |
| B | 月が行・科目が列 | 月を集計 |
| C | 2列（科目 / 金額） | 座標ベース抽出の結果 |

### 座標ベース抽出

日本語PDFではラベルと数値が別テキストブロックに分離することがあるため、  
x座標でラベル（左列）と数値（右列）を照合して自動結合します。

### キーワードマップ（抜粋）

| 日本語 | フィールド |
|--------|-----------|
| 売上高, 営業収益, 売上収入 | `revenue` |
| 売上原価, 製造原価, 原価 | `cost_of_goods_sold` |
| 売上総利益, 粗利 | `gross_profit` |
| 販売費, 販管費 | `selling_expenses` |
| 営業利益, 事業利益 | `operating_income` |
| 当期純利益, 最終利益, 純損益 | `net_income` |

---

## Excelローダー

`financial_analysis/excel_loader.py` — openpyxl を使用

### シート自動選択

シート名に **損益 / PL / P&L / 売上** を含むシートを優先選択。

### テーブル解析パターン

| パターン | 形式 |
|----------|------|
| A | 科目が行、月が列（合計列を自動検出） |
| B | 月が行、科目が列 |

### 合計列の自動検出

- 「合計」「計」「累計」「Total」などを含む列
- 月数値列の最大値を持つ列

### シート名を指定する場合

```python
data = load_financial_data("月次PL.xlsx", sheet_name="損益計算書")
```

---

## Wordローダー

`financial_analysis/word_loader.py` — python-docx を使用

### 解析手順

1. **表（Table）優先**: ドキュメント内のすべてのテーブルを走査
2. **段落テキスト（フォールバック）**: テーブルがない場合は本文テキストを解析

### 注意

- `.docx` のみ対応。古い `.doc` 形式は対応不可。
- `.doc` を指定した場合、`ValueError` が発生し変換方法を案内します。

---

## Google Driveローダー

`financial_analysis/google_drive_loader.py`

### 対応URLパターン

| URLの形式 | ダウンロード形式 |
|-----------|----------------|
| `drive.google.com/file/d/{ID}` | ファイルをそのままダウンロード |
| `docs.google.com/spreadsheets/d/{ID}` | Excel形式でエクスポート |
| `docs.google.com/document/d/{ID}` | Word形式でエクスポート |

### 公開ファイル（サービスアカウント不要）

```python
from financial_analysis import GoogleDriveLoader

loader = GoogleDriveLoader()
data = loader.load_from_url(
    "https://drive.google.com/file/d/xxxxx/view?usp=sharing",
    company_name="株式会社〇〇",
    period="2024年3月期",
    unit=1.0,
)
```

### 非公開ファイル（サービスアカウント）

```python
loader = GoogleDriveLoader(credentials_path="service_account.json")
data = loader.load_from_url("https://drive.google.com/file/d/xxxxx/view")
```

### 注意

- プロキシ環境（社内ネットワーク等）では 403 エラーが発生することがあります。
- その場合はファイルをローカルにダウンロードして `load_financial_data()` に渡してください。
- **Google Colab を使用すると、Drive を直接マウントできるためプロキシ問題を回避できます。**
