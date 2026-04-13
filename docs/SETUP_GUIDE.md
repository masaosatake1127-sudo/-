# 財務分析ツール — セットアップ・操作手順書

---

## 目次

1. [環境準備](#1-環境準備)
2. [インストール](#2-インストール)
3. [Colabで使う（タブレット推奨）](#3-google-colabで使うタブレット推奨)
4. [CLIで使う（PC）](#4-cliで使うpc)
5. [WebUIで使う（PC）](#5-webui-streamlitで使うpc)
6. [ファイルが正しく読み込めない場合](#6-ファイルが正しく読み込めない場合)
7. [対応ファイル形式と準備のポイント](#7-対応ファイル形式と準備のポイント)

---

## 1. 環境準備

### Colabを使う場合（タブレット・PC）

- Googleアカウントがあれば追加インストール不要
- 手順3へ進んでください

### ローカル（PC）で動かす場合

- Python 3.9 以上
- pip が使用可能なこと

---

## 2. インストール

```bash
# リポジトリのクローン（またはダウンロード）
git clone <リポジトリURL>
cd <プロジェクトフォルダ>

# 依存パッケージのインストール
pip install -r requirements.txt
```

`requirements.txt` の内容:

```
pytest>=7.0
pymupdf>=1.23
openpyxl>=3.1
python-docx>=1.0
requests>=2.31
google-api-python-client>=2.0
google-auth>=2.0
streamlit>=1.30
```

---

## 3. Google Colabで使う（タブレット推奨）

タブレットやスマートフォンでも Google Drive のファイルを直接分析できます。

### 手順

#### ステップ1: Colabを開く

1. ブラウザで [https://colab.research.google.com/](https://colab.research.google.com/) にアクセス
2. 「ファイル」→「ノートブックをアップロード」
3. `financial_analysis_colab.ipynb` を選択してアップロード

> Googleドライブに保存済みの場合は「ドライブ」タブからも開けます。

#### ステップ2: ライブラリをインストール（セル①）

```python
# セル①を実行（▶ボタンをタップ）
!pip install pymupdf openpyxl python-docx
```

> **初回のみ実行** が必要です。ランタイムが変わると再実行が必要になります。

#### ステップ3: コードを読み込む（セル②）

セル②を実行します。財務分析コードがすべてメモリに読み込まれます。

#### ステップ4: Google Driveをマウント（セル③）

```python
# セル③を実行
from google.colab import drive
drive.mount('/content/drive')
```

1. 実行すると認証リンクが表示される
2. リンクをタップしてGoogleアカウントにログイン
3. 表示されたコードをコピーして入力ボックスに貼り付け
4. 「ドライブがマウントされました」と表示されれば完了

#### ステップ5: ファイルマネージャーを起動（セル④）

```python
# セル④を実行
scan_drive('/content/drive/MyDrive', max_depth=3)
```

実行すると Drive 内の対応ファイルが番号付きで表示されます:

```
📄  1. 月次PL_2024.pdf        /content/drive/MyDrive/財務/月次PL_2024.pdf
📊  2. 決算書.xlsx             /content/drive/MyDrive/決算/決算書.xlsx
📝  3. 財務報告書.docx         /content/drive/MyDrive/報告/財務報告書.docx

合計 3 件のファイルが見つかりました
```

> `max_depth` を増やすと深い階層まで検索します（デフォルト: 3）

#### ステップ6: ファイルを選択して分析（セル⑤）

```python
FILE_NUMBER = 2          # 分析したいファイルの番号
COMPANY_NAME = "株式会社〇〇"   # 企業名（省略可）
PERIOD = "2024年3月期"   # 会計期間（省略可）
UNIT = 1.0               # 金額単位（千円=1000, 百万円=1000000）
SHEET_NAME = None        # Excelのシート名（省略=自動選択）
```

セル⑤を実行すると分析結果がノートブック上に表示されます。

#### ステップ7（オプション）: 複数ファイルを一括分析（セル⑥）

```python
FILE_NUMBERS = [1, 2, 3]   # 分析したいファイルの番号リスト
```

---

## 4. CLIで使う（PC）

### サンプルデータで試す

```bash
python examples/run_analysis.py
```

### ローカルファイルを分析

```bash
# PDF
python examples/run_analysis.py --input 決算書.pdf

# Excel（千円単位、シート名指定）
python examples/run_analysis.py \
    --input 月次PL.xlsx \
    --company "株式会社〇〇" \
    --period "2024年3月期" \
    --unit 1000 \
    --sheet "損益計算書"

# Word
python examples/run_analysis.py --input 財務報告.docx
```

### レポートをファイルに保存

```bash
# Markdownで保存
python examples/run_analysis.py \
    --input 決算書.pdf \
    --format markdown \
    --output report.md

# テキストで保存
python examples/run_analysis.py \
    --input 決算書.pdf \
    --output report.txt
```

### Google Drive から分析

```bash
# 公開ファイル（共有リンクが有効なファイル）
python examples/run_analysis.py \
    --gdrive "https://drive.google.com/file/d/xxxxx/view?usp=sharing"

# 非公開ファイル（サービスアカウントが必要）
python examples/run_analysis.py \
    --gdrive "https://drive.google.com/file/d/xxxxx/view" \
    --credentials service_account.json
```

---

## 5. WebUI (Streamlit)で使う（PC）

### 起動

```bash
streamlit run app.py
```

ブラウザが自動的に `http://localhost:8501` を開きます。

### 操作手順

1. **サイドバー**で設定を入力:
   - 企業名（省略可）
   - 会計期間（省略可）
   - 金額単位（円 / 千円 / 百万円）
   - Excelシート名（省略可）
   - レポート形式（テキスト / Markdown）

2. **ファイルアップロードエリア**にファイルをドラッグ＆ドロップ、またはクリックして選択
   - 対応形式: PDF / Excel (.xlsx .xls) / Word (.docx)

3. 分析結果が自動表示されます:
   - 抽出した主要数値（5項目）
   - 総合評価スコア
   - タブ別の詳細指標（収益性 / 安全性 / 効率性 / 成長性 / CF）

4. **レポートをダウンロード**ボタンでファイル保存

---

## 6. ファイルが正しく読み込めない場合

### 売上高が 0 になる

科目名が標準的な表記と異なる可能性があります。

**CLIでデバッグ確認:**

```bash
python examples/run_analysis.py --input 決算書.pdf --debug
```

**Colabでデバッグ確認（セル⑦）:**

セル⑦を実行すると、シート名・先頭行・抽出テキストが表示されます。

**対処方法:**
- ファイル内の科目名を確認し、以下のいずれかに合わせる:

| 標準表記（認識可能） |
|---------------------|
| 売上高 / 営業収益 / 売上収入 |
| 売上原価 / 製造原価 / 原価 |
| 売上総利益 / 粗利 |
| 販売費 / 販管費 / 販売費及び一般管理費 |
| 営業利益 / 事業利益 |
| 当期純利益 / 最終利益 / 純損益 |

### Excelで複数シートがある

```bash
# シート名を明示指定
python examples/run_analysis.py --input 月次PL.xlsx --sheet "損益計算書"
```

Streamlit の場合はサイドバーの「Excelシート名」欄に入力。

### PDFの数値が認識されない

- スキャンPDF（画像PDF）は対応していません。テキスト選択ができるPDFが必要です。
- △▲ や (xxx) 形式の負数表記は自動的に負値に変換されます。

### `.doc` 形式のWordファイル

`.doc` は非対応です。Word で開き「名前を付けて保存」→「.docx 形式」で保存してください。

### Google Drive にアクセスできない

プロキシ環境では接続が遮断されることがあります。  
→ ファイルをローカルにダウンロードし、`--input` オプションで指定してください。  
→ またはGoogle Colabを使用すると（Drive直接マウント）プロキシ問題を回避できます。

---

## 7. 対応ファイル形式と準備のポイント

### PDF

- テキストPDF（コピー＆ペーストができるもの）が対象
- 1ページに収まる損益計算書が最も精度が高い
- 縦書きや特殊フォントは認識精度が下がることがあります

### Excel (.xlsx / .xls / .xlsm)

| 推奨レイアウト | 説明 |
|---------------|------|
| **パターンA**（推奨） | 科目が行、月が列（合計列あり） |
| パターンB | 月が行、科目が列 |

- 先頭行や先頭列にタイトルがある場合も自動スキップします
- 金額単位が「千円」の場合は `--unit 1000` を指定してください

### Word (.docx)

- 表形式（Wordのテーブル）のデータを優先して読み込みます
- 箇条書き・段落のみのドキュメントでもフォールバック解析します

---

## よくある使用例まとめ

```bash
# 1. まずサンプルで動作確認
python examples/run_analysis.py

# 2. PDFを分析してMarkdown出力
python examples/run_analysis.py -i 決算書.pdf --format markdown -o report.md

# 3. 千円単位のExcelを分析
python examples/run_analysis.py -i 月次PL.xlsx --unit 1000

# 4. 抽出内容をデバッグ確認
python examples/run_analysis.py -i 月次PL.xlsx --debug

# 5. WebUIを起動
streamlit run app.py
```
