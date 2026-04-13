# 実行インターフェース

財務分析ツールには 3 つの実行方法があります。

---

## 1. CLIスクリプト (`examples/run_analysis.py`)

ターミナル / コマンドプロンプトから実行する方法です。

### 基本的な使い方

```bash
# サンプルデータで実行（ファイル不要）
python examples/run_analysis.py

# ローカルファイルを指定
python examples/run_analysis.py --input 決算書.pdf
python examples/run_analysis.py --input 月次PL.xlsx
python examples/run_analysis.py --input 財務報告.docx

# Google Drive URL を指定
python examples/run_analysis.py --gdrive "https://drive.google.com/file/d/xxxxx/view?usp=sharing"
```

### オプション一覧

| オプション | 短縮 | 説明 | デフォルト |
|-----------|------|------|-----------|
| `--input FILE` | `-i` | ローカルファイルのパス | — |
| `--gdrive URL` | `-g` | Google Drive 共有リンク | — |
| `--credentials JSON` | — | サービスアカウントキーJSON | — |
| `--company NAME` | — | 企業名 | ファイル名 |
| `--period PERIOD` | — | 会計期間（例: 2024年3月期） | "" |
| `--unit MULTIPLIER` | — | 金額単位倍率（千円=1000） | 1.0 |
| `--sheet SHEET_NAME` | — | Excelのシート名 | 自動選択 |
| `--format` | — | `text` or `markdown` | text |
| `--output FILE` | — | 出力ファイルパス（省略=標準出力） | 標準出力 |
| `--debug` | — | 抽出テキスト・表を表示 | — |

### 実行例

```bash
# 千円単位のExcelを指定し、Markdownで保存
python examples/run_analysis.py \
    --input 月次PL.xlsx \
    --company "株式会社〇〇" \
    --period "2024年3月期" \
    --unit 1000 \
    --format markdown \
    --output report.md

# 抽出確認（科目が正しく認識されているか確認）
python examples/run_analysis.py --input 決算書.pdf --debug

# Googleスプレッドシート（サービスアカウント不要の公開ファイル）
python examples/run_analysis.py \
    --gdrive "https://docs.google.com/spreadsheets/d/xxxxx/edit"
```

---

## 2. Streamlit Web UI (`app.py`)

ブラウザからファイルをドラッグ＆ドロップして分析する方法です。  
**PCでの利用を推奨**（モバイル・タブレットでは操作性が限られます）。

### 起動方法

```bash
pip install streamlit
streamlit run app.py
# ブラウザが自動的に http://localhost:8501 を開きます
```

### 機能

- PDF / Excel (.xlsx .xls .xlsm) / Word (.docx) のアップロード
- サイドバーで企業名・会計期間・金額単位・シート名を設定
- 抽出した主要数値（5項目）のメトリクス表示
- タブ別の詳細指標表示（収益性 / 安全性 / 効率性 / 成長性 / CF）
- テキスト or Markdown 形式でレポートをダウンロード

### 画面構成

```
[サイドバー]           [メインエリア]
・企業名               ファイルアップロードエリア
・会計期間             ─────────────────────
・金額単位             抽出結果サマリー（5指標）
・シート名             ─────────────────────
・レポート形式         総合評価スコア + プログレスバー
                      タブ: 収益性/安全性/効率性/成長性/CF
                      ─────────────────────
                      レポートダウンロードボタン
```

---

## 3. Google Colab ノートブック (`financial_analysis_colab.ipynb`)

タブレット・スマートフォンでも利用可能。Google Drive のファイルを直接分析できます。

### セル構成

| セル | 内容 |
|------|------|
| ① | ライブラリインストール (`pymupdf`, `openpyxl`, `python-docx`) |
| ② | 財務分析コード全文（inline） |
| ③ | Google Drive マウント |
| ④ | **ファイルマネージャー** — `scan_drive()` でDrive内を検索・番号表示 |
| ⑤ | `FILE_NUMBER` で1ファイル選択・分析 |
| ⑥ | `FILE_NUMBERS` リストで複数ファイル一括分析 |
| ⑦ | デバッグ確認（シート名・先頭行・テキスト） |

### ファイルマネージャーの使い方（セル④）

```
セル④を実行すると:

📄  1. 月次PL_2024.pdf        /content/drive/MyDrive/財務/月次PL_2024.pdf
📊  2. 決算書.xlsx             /content/drive/MyDrive/決算/決算書.xlsx
📝  3. 財務報告書.docx         /content/drive/MyDrive/報告/財務報告書.docx

合計 3 件のファイルが見つかりました
```

```python
# セル⑤: 番号で選択
FILE_NUMBER = 2       # → 決算書.xlsx を分析
COMPANY_NAME = "株式会社〇〇"
PERIOD = "2024年3月期"
UNIT = 1.0
```

```python
# セル⑥: 複数ファイルを一括分析
FILE_NUMBERS = [1, 2, 3]
```

### Colabを開く手順

1. [Google Colab](https://colab.research.google.com/) にアクセス
2. 「ファイル」→「ノートブックをアップロード」→ `financial_analysis_colab.ipynb` を選択
3. または GitHub URL から直接開く

---

## 方法の選択ガイド

| 状況 | 推奨方法 |
|------|---------|
| PC でターミナルが使える | CLI スクリプト |
| PC でブラウザから使いたい | Streamlit Web UI |
| タブレット / スマートフォン | Google Colab ノートブック |
| Google Drive のファイルを分析 | Colab（Driveマウント）|
| バッチ処理・自動化 | CLI スクリプト |
| 複数ファイルをまとめて分析 | Colab（セル⑥）|
