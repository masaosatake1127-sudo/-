# よくある質問（FAQ）

---

## ファイル読み込み関連

### Q: 売上高が 0 になる

**原因:** ファイル内の科目名が認識できていない可能性があります。

**対処手順:**

1. デバッグモードで中身を確認する
   ```bash
   python examples/run_analysis.py --input 決算書.pdf --debug
   ```
   Colabの場合はセル⑦を実行。

2. 出力されたテキストに「売上高」「売上」などが含まれているか確認。

3. 含まれている場合 → キーワードマップに追加依頼。  
   含まれていない場合 → ファイルがスキャンPDFの可能性あり（次のQへ）。

---

### Q: PDFが読み込めない・数値がすべて0になる

**原因:** スキャンPDF（画像PDF）は非対応です。

**確認方法:** PDF上でテキストを選択できるか試してください。選択できない場合はスキャンPDFです。

**対処:** Adobe AcrobatなどでOCR処理を行い、テキストPDFに変換してください。

---

### Q: Excelで正しいシートが読まれない

**原因:** シート名に「損益」「PL」「P&L」「売上」が含まれていない場合、先頭シートが使われます。

**対処:**
```bash
# シート名を明示指定
python examples/run_analysis.py --input 月次PL.xlsx --sheet "損益計算書"
```
Streamlit の場合はサイドバーの「Excelシート名」欄に入力。  
Colabの場合はセル⑤の `SHEET_NAME = "損益計算書"` に入力。

---

### Q: 金額がおかしい（100倍・1000倍になっている）

**原因:** ファイルの金額単位（千円・百万円）と設定が合っていません。

**対処:**
```bash
# 千円単位のファイルの場合
python examples/run_analysis.py --input 月次PL.xlsx --unit 1000

# 百万円単位のファイルの場合
python examples/run_analysis.py --input 月次PL.xlsx --unit 1000000
```
Colabの場合はセル⑤の `UNIT = 1000` を変更。

---

### Q: `.doc` ファイルが読み込めない

**原因:** 旧Word形式（`.doc`）は非対応です。

**対処:** Wordで開き「名前を付けて保存」→「Word文書 (.docx)」で保存してください。

---

### Q: Google Drive からファイルが取得できない（403エラー）

**原因:** プロキシ（社内ネットワーク等）がGoogle Driveへの接続を遮断しています。

**対処:**
- ファイルをローカルにダウンロードして `--input` で指定する
- または **Google Colab** を使用する（Drive を直接マウントするためプロキシ不要）

---

## Colab 関連

### Q: セルを実行しても何も起きない・エラーになる

**確認手順:**
1. セル①（ライブラリインストール）を実行したか確認
2. セル②（分析コード読み込み）を実行したか確認
3. ランタイムをリセットして最初からやり直す（「ランタイム」→「ランタイムを再起動」）

---

### Q: Drive のマウントで認証がうまくいかない

**対処:**
1. セル③を再実行
2. 表示されたリンクをタップ → Googleアカウントを選択
3. 「Googleドライブへのアクセスを許可」→ 表示されたコードをコピーして入力欄に貼り付け

---

### Q: ファイルマネージャー（セル④）でファイルが見つからない

**確認:**
- `SEARCH_ROOT` の設定を確認（デフォルト: `/content/drive/MyDrive`）
- `SEARCH_DEPTH` を増やす（デフォルト: 3 → 5 など）
- 対応形式（PDF / xlsx / xls / xlsm / docx）のファイルが存在するか確認

---

## 分析結果関連

### Q: 成長率がすべて「データなし」と表示される

**原因:** 前期データがないと成長率は算出できません。

**対処:** 現在は前期データの入力機能をCLI・Colabでは未実装です。  
ライブラリを直接使う場合は以下のように前期データを渡せます:

```python
from financial_analysis.models import FinancialData

data = FinancialData(
    company_name="株式会社〇〇",
    income_statement=current_is,
    balance_sheet=current_bs,
    cash_flow_statement=current_cf,
    previous_income_statement=prev_is,   # 前期データ
    previous_balance_sheet=prev_bs,
)
```

---

### Q: 総合スコアの計算方法を知りたい

| カテゴリ | 満点 | 基準 |
|----------|------|------|
| 収益性 | 30点 | 営業利益率 ≥15%→30点, ≥5%→20点, ≥0%→10点 |
| 安全性 | 30点 | 自己資本比率(15点) + 流動比率(15点) |
| 効率性 | 20点 | 総資産回転率 ≥1.5→20点, ≥0.8→13点 |
| CF | 20点 | FCF≥0 かつ CFマージン≥10%→20点 |

詳細は `docs/03_analyzer_report.md` を参照。

---

### Q: レポートをファイルに保存したい

```bash
# テキスト形式
python examples/run_analysis.py --input 決算書.pdf --output report.txt

# Markdown形式
python examples/run_analysis.py --input 決算書.pdf --format markdown --output report.md
```

Streamlit の場合は画面下部の「ダウンロード」ボタンを使用。

---

## インストール関連

### Q: `pymupdf` のインストールでエラーが出る

```bash
pip install pymupdf --upgrade
```

それでも失敗する場合:
```bash
pip install PyMuPDF
```

### Q: `pdfplumber` を使いたい

本ツールは `pdfplumber` ではなく `PyMuPDF (fitz)` を使用しています。  
（`pdfplumber` は一部環境で `_cffi_backend` エラーが発生するため変更しました）

---

## テスト関連

### Q: テストを実行する方法

```bash
# 全テスト実行
pytest tests/ -v

# 特定ファイルのみ
pytest tests/test_models.py -v
```

### Q: テストが失敗する

```bash
# 依存パッケージを再インストール
pip install -r requirements.txt

# キャッシュをクリアして再実行
pytest tests/ --cache-clear
```
