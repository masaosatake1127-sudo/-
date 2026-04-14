# 変更履歴（Changelog）

すべての変更はブランチ `claude/financial-analysis-hhMXm` で管理されています。

---

## [現在] — 2026-04-14

### 追加
- `docs/faq.md` — よくある質問と対処法
- `docs/changelog.md` — 変更履歴（このファイル）
- `docs/test.md` — テスト仕様・実行方法
- `docs/roadmap.md` — 今後の機能追加計画

---

## v0.7 — ドキュメント整備・コードレビュー

### 追加
- `docs/skill.md` — 機能・技術スタック一覧（Claude Project用）
- `docs/` 全7ファイル（01_models〜SETUP_GUIDE）
- Colabノートブック セル⑧: ドキュメントZIPダウンロード機能

### 改善（コードレビュー対応）
- `KEYWORD_MAP` に不足キーを7件追加
  （`当期利益`・`営業損失`・`経常損失`・`税引前当期純損失`・`受取利息`・`法人税住民税及び事業税`・`売上収入`）
- `TOTAL_KEYWORDS` 定数と `_resolve_total_col()` ヘルパーを抽出
  → `load_excel` / `load_word` の重複ロジックを共通化
- `_build_income` の未使用 `unit` 引数を削除
- `load_word` に全フィールド取得後の早期終了を追加
- `_fm_files` チェックを `dir()` から `globals().get()` に修正
- `pdf_loader.py` の `_KEYWORD_MAP` に `売上収入` を追加

### 修正（ドキュメント）
- `SETUP_GUIDE.md` の重複キーワードテーブルをクロスリンクに置換
- scan_drive 出力例の重複を `05_interfaces.md` へのリンクに統合

---

## v0.6 — Google Colab ファイルマネージャー

### 追加
- Colabノートブック セル④: `scan_drive()` でDrive内を再帰検索
  - PDF/Excel/Wordファイルをアイコン付き番号リストで表示（📄📊📝）
- Colabノートブック セル⑤: 番号入力で1ファイル選択・分析
- Colabノートブック セル⑥: `FILE_NUMBERS` リストで複数ファイル一括分析
- Colabノートブック セル⑦: デバッグ確認（シート名・先頭行・テキスト）

---

## v0.5 — ドキュメント初版

### 追加
- `docs/` ディレクトリと7つのmdファイル

---

## v0.4 — Google Colab ノートブック

### 追加
- `financial_analysis_colab.ipynb` — タブレット向けColab環境
  - ライブラリインストール・コード読み込み・Driveマウントセル
  - 単一ファイル分析・レポート出力機能

---

## v0.3 — Streamlit Web UI

### 追加
- `app.py` — ブラウザからファイルをアップロードして分析するWebアプリ
  - 対応形式: PDF / Excel (.xlsx .xls) / Word (.docx)
  - 抽出数値のメトリクス表示
  - タブ別詳細指標（収益性/安全性/効率性/成長性/CF）
  - テキスト・Markdown形式のレポートダウンロード

---

## v0.2 — Google Drive 対応

### 追加
- `financial_analysis/google_drive_loader.py`
  - 公開ファイルの直接ダウンロード（ウイルススキャントークン対応）
  - サービスアカウントによる非公開ファイルアクセス
  - スプレッドシート → Excel / ドキュメント → Word 形式でエクスポート
- `examples/run_analysis.py` に `--gdrive` / `--credentials` オプション追加

---

## v0.1.1 — Excel・Word 対応

### 追加
- `financial_analysis/excel_loader.py` — openpyxl ベース
  - シート自動選択（損益/PL/P&L/売上）
  - パターンA（科目が行・月が列）/ パターンB（月が行・科目が列）
  - 合計列の自動検出
- `financial_analysis/word_loader.py` — python-docx ベース
  - 表形式優先・段落テキストへのフォールバック
- `examples/test_monthly_pl.xlsx` / `test_monthly_pl.docx` サンプル追加

---

## v0.1 — 初期リリース

### 追加
- `financial_analysis/models.py` — 財務諸表データモデル（dataclass）
  - `IncomeStatement` / `BalanceSheet` / `CashFlowStatement` / `FinancialData`
  - `__post_init__` による自動計算（粗利・営業利益・当期純利益 等）
- `financial_analysis/ratios.py` — 財務比率計算
  - 収益性・安全性・効率性・成長性・CFの5カテゴリ
  - `_safe_divide()` / `_pct()` ゼロ除算ガード
- `financial_analysis/analyzer.py` — 評価コメント + 総合スコア（0〜100）
- `financial_analysis/report.py` — テキスト / Markdown レポート生成
- `financial_analysis/pdf_loader.py` — PyMuPDF ベースPDFローダー
  - 座標ベース抽出（ラベルと数値が分離した日本語PDFに対応）
  - △▲/(xxx) 形式の負数表記を自動変換
- `financial_analysis/file_loader.py` — 統合ローダー（拡張子自動判定）
- `examples/run_analysis.py` — CLIスクリプト
- `examples/sample_data.py` — サンプルデータ（株式会社サンプルテック）
- `tests/` — 単体テスト27件（models / ratios / analyzer）
- `requirements.txt`
