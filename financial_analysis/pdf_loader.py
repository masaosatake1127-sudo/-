"""
PDF財務データローダー

PDFから損益計算書の月別残高推移を抽出し、FinancialDataに変換します。

対応フォーマット:
  - 縦軸=勘定科目、横軸=月（4月〜3月 + 合計）の表形式PDF
  - テキストベースのPDF（スキャン画像PDFは非対応）

使い方:
    loader = PdfIncomeStatementLoader()
    data = loader.load("決算書.pdf", company_name="株式会社〇〇")
    print(data.income_statement.revenue)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from .models import (
    BalanceSheet,
    CashFlowStatement,
    FinancialData,
    IncomeStatement,
)

# ---------------------------------------------------------------
# 勘定科目キーワードマッピング
# 「PDFに出てくる可能性のある表記」→「内部フィールド名」
# ---------------------------------------------------------------
_KEYWORD_MAP: Dict[str, str] = {
    # 売上高
    "売上高": "revenue",
    "売上": "revenue",
    "収益合計": "revenue",
    "営業収益": "revenue",
    "売上収入": "revenue",
    # 売上原価
    "売上原価": "cost_of_goods_sold",
    "原価合計": "cost_of_goods_sold",
    "製造原価": "cost_of_goods_sold",
    # 売上総利益
    "売上総利益": "gross_profit",
    "粗利": "gross_profit",
    "粗利益": "gross_profit",
    # 販売費
    "販売費": "selling_expenses",
    "販売費及び一般管理費": "selling_and_admin",  # 合算の場合
    "販管費": "selling_and_admin",
    # 一般管理費
    "一般管理費": "general_admin_expenses",
    "管理費": "general_admin_expenses",
    # 営業利益
    "営業利益": "operating_income",
    "営業損益": "operating_income",
    "営業損失": "operating_income",
    # 営業外収益
    "営業外収益": "non_operating_income",
    "受取利息": "non_operating_income",
    # 営業外費用
    "営業外費用": "non_operating_expenses",
    "支払利息": "non_operating_expenses",
    # 経常利益
    "経常利益": "ordinary_income",
    "経常損益": "ordinary_income",
    "経常損失": "ordinary_income",
    # 特別利益
    "特別利益": "extraordinary_income",
    # 特別損失
    "特別損失": "extraordinary_losses",
    "特別費用": "extraordinary_losses",
    # 税引前利益
    "税引前当期純利益": "income_before_tax",
    "税引前当期純損失": "income_before_tax",
    "税引前利益": "income_before_tax",
    # 法人税等
    "法人税": "income_tax",
    "法人税、住民税及び事業税": "income_tax",
    "法人税等": "income_tax",
    # 当期純利益
    "当期純利益": "net_income",
    "当期純損失": "net_income",
    "当期利益": "net_income",
    "純利益": "net_income",
}

# 月名→インデックス
_MONTH_PATTERN = re.compile(r"(\d{1,2})月")


def _parse_number(text: str) -> Optional[float]:
    """数値文字列をfloatに変換（カンマ・△・▲・括弧負号に対応）"""
    if not text:
        return None
    t = text.strip().replace(",", "").replace("，", "").replace(" ", "")
    if not t or t in ("-", "―", "—", "－"):
        return 0.0
    negative = False
    # △▲ または (xxx) 形式の負値
    if t.startswith(("△", "▲", "▽")):
        negative = True
        t = t[1:]
    elif t.startswith("(") and t.endswith(")"):
        negative = True
        t = t[1:-1]
    elif t.startswith("（") and t.endswith("）"):
        negative = True
        t = t[1:-1]
    try:
        val = float(t)
        return -val if negative else val
    except ValueError:
        return None


class PdfIncomeStatementLoader:
    """
    PDFから月別損益計算書を読み込み FinancialData を返すローダー。

    想定する表フォーマット（どちらも対応）:

    [パターンA] 科目が行、月が列
        勘定科目 | 4月 | 5月 | ... | 3月 | 合計
        売上高   | 100 | 110 | ... | 120 | 1230
        ...

    [パターンB] 月が行、科目が列
        月  | 売上高 | 売上原価 | ...
        4月 | 100   | 40      | ...
        ...
    """

    def load(
        self,
        pdf_path: str,
        company_name: str = "",
        period: str = "",
        unit: float = 1.0,
    ) -> FinancialData:
        """
        PDFを読み込んで FinancialData を返す。

        Args:
            pdf_path:     PDFファイルのパス
            company_name: 企業名（省略時はファイル名）
            period:       会計期間文字列（例: "2024年3月期"）
            unit:         金額単位の倍率（千円単位なら1000, 百万円なら1000000）
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

        if not company_name:
            company_name = path.stem

        raw_text, tables = self._extract_from_pdf(str(path))

        # テーブル抽出を優先、なければテキストから試みる
        fields: Dict[str, float] = {}
        if tables:
            fields = self._parse_tables(tables, unit)
        if not fields:
            fields = self._parse_raw_text(raw_text, unit)

        if not fields:
            raise ValueError(
                "PDFから財務データを抽出できませんでした。\n"
                "・テキストベースのPDFか確認してください（スキャン画像PDFは非対応）\n"
                "・--debug オプションで抽出テキストを確認できます"
            )

        # period が不明なら本文から推測
        if not period:
            period = self._guess_period(raw_text)

        income_stmt = self._build_income_statement(fields, period)
        balance_sheet = BalanceSheet()       # PDFに貸借・CF情報がなければ空
        cash_flow = CashFlowStatement(net_income=income_stmt.net_income or 0.0)

        return FinancialData(
            company_name=company_name,
            income_statement=income_stmt,
            balance_sheet=balance_sheet,
            cash_flow_statement=cash_flow,
        )

    # ------------------------------------------------------------------
    # PDF テキスト・テーブル抽出
    # ------------------------------------------------------------------

    def _extract_from_pdf(self, pdf_path: str) -> Tuple[str, List[List[List[str]]]]:
        """PyMuPDF でテキストと表データを抽出する"""
        all_text_parts: List[str] = []
        all_tables: List[List[List[str]]] = []

        with fitz.open(pdf_path) as doc:
            for page in doc:
                # テキスト抽出
                all_text_parts.append(page.get_text())

                # 表抽出（PyMuPDF 1.23+ の find_tables を利用）
                try:
                    tabs = page.find_tables()
                    for tab in tabs:
                        rows = tab.extract()
                        if rows:
                            all_tables.append(rows)
                except AttributeError:
                    pass  # 古いバージョンでは非対応

                # 座標ベースの列マッチングテーブルも生成する
                coord_table = self._extract_by_coordinates(page)
                if coord_table:
                    all_tables.append(coord_table)

        return "\n".join(all_text_parts), all_tables

    def _extract_by_coordinates(self, page) -> List[List[str]]:
        """
        ワード座標を使って「科目列」と「合計列」をy座標でマッチングする。
        科目名（日本語）と数値が別ブロックになっているPDFへの対応。
        """
        words = page.get_text("words")  # (x0,y0,x1,y1, text, block, line, word)
        if not words:
            return []

        # ページ幅の中央より左=ラベル列、右=数値列と仮定
        page_width = page.rect.width
        mid_x = page_width * 0.4  # 40%より左をラベルとみなす

        label_words: Dict[int, List[str]] = {}  # y_bucket -> [words]
        number_words: Dict[int, List[str]] = {}

        for x0, y0, x1, y1, text, *_ in words:
            y_key = int(y0 / 6) * 6  # 6pt単位でバケット化
            text = text.strip()
            if not text:
                continue
            if x0 < mid_x:
                label_words.setdefault(y_key, []).append(text)
            else:
                number_words.setdefault(y_key, []).append(text)

        rows: List[List[str]] = []
        # ラベルと数値が同じy_keyにあるものをペアにする
        for y_key in sorted(label_words.keys()):
            label = " ".join(label_words[y_key])
            nums = number_words.get(y_key, [])
            if not nums:
                # 近い行の数値を探す（±12pt以内）
                for dy in (6, 12, -6, -12):
                    nums = number_words.get(y_key + dy, [])
                    if nums:
                        break
            # 最後の数値を「合計」として採用
            total_num = nums[-1] if nums else ""
            rows.append([label, total_num])

        return rows

    def extract_text_for_debug(self, pdf_path: str) -> str:
        """デバッグ用: PDFから抽出した生テキストと座標情報を返す"""
        lines = []
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                lines.append(f"=== ページ {i+1} テキスト ===")
                lines.append(page.get_text())
                lines.append(f"\n=== ページ {i+1} 座標ベース抽出 ===")
                rows = self._extract_by_coordinates(page)
                for row in rows:
                    lines.append(f"  {row[0]!r:30s} → {row[1]!r}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # テーブルパース
    # ------------------------------------------------------------------

    def _parse_tables(
        self, tables: List[List[List[str]]], unit: float
    ) -> Dict[str, float]:
        """抽出されたテーブルリストから財務フィールドを読み取る"""
        fields: Dict[str, float] = {}

        for table in tables:
            if not table or len(table) < 2:
                continue

            # --- パターンC: 2列テーブル [科目名, 金額] (座標ベース抽出の結果) ---
            if all(len(row) == 2 for row in table):
                found_any = False
                for row in table:
                    label = str(row[0] or "").strip()
                    field = self._match_keyword(label)
                    if field:
                        val = _parse_number(str(row[1] or ""))
                        if val is not None and field not in fields:
                            fields[field] = val * unit
                            found_any = True
                if found_any:
                    continue

            header = [str(c or "").strip() for c in table[0]]

            # --- パターンA: 科目が行、月/合計が列 ---
            total_col = self._find_total_column(header)
            if total_col is not None:
                for row in table[1:]:
                    if not row or len(row) <= total_col:
                        continue
                    label = str(row[0] or "").strip()
                    field = self._match_keyword(label)
                    if field:
                        val = _parse_number(str(row[total_col] or ""))
                        if val is not None:
                            fields[field] = val * unit
                continue

            # --- パターンB: 月が行、科目が列 ---
            col_fields = {}
            for ci, h in enumerate(header):
                f = self._match_keyword(h)
                if f:
                    col_fields[ci] = f

            if col_fields:
                totals: Dict[str, float] = {}
                for row in table[1:]:
                    label = str(row[0] or "").strip() if row else ""
                    is_total = any(k in label for k in ("合計", "累計", "年計", "通期"))
                    for ci, f in col_fields.items():
                        if ci < len(row):
                            val = _parse_number(str(row[ci] or ""))
                            if val is not None:
                                if is_total:
                                    totals[f] = val * unit
                                else:
                                    totals[f] = totals.get(f, 0.0) + val * unit
                fields.update(totals)

        return fields

    def _find_total_column(self, header: List[str]) -> Optional[int]:
        """ヘッダー行から「合計」列のインデックスを返す"""
        for i, h in enumerate(header):
            if any(k in h for k in ("合計", "累計", "年計", "通期", "決算")):
                return i
        # 月ヘッダーが並んでいれば最後の列を合計と見なす
        month_cols = [i for i, h in enumerate(header) if _MONTH_PATTERN.search(h)]
        if len(month_cols) >= 3:
            return max(month_cols)
        return None

    # ------------------------------------------------------------------
    # テキストパース（テーブル抽出失敗時のフォールバック）
    # ------------------------------------------------------------------

    def _parse_raw_text(self, text: str, unit: float) -> Dict[str, float]:
        """生テキストから科目名と金額を正規表現で抜き出す"""
        fields: Dict[str, float] = {}
        # 「科目名 ... 数値」のパターン
        number_re = re.compile(
            r"([\u3000-\u9fff\uff00-\uffef\u4e00-\u9fff]+)"   # 科目名（漢字・ひらがな）
            r"[\s\u3000]*"
            r"([△▲▽(（]?\s*[\d,，]+\s*[)）]?)"               # 金額
        )
        for m in number_re.finditer(text):
            label = m.group(1).strip()
            field = self._match_keyword(label)
            if field and field not in fields:
                val = _parse_number(m.group(2))
                if val is not None:
                    fields[field] = val * unit
        return fields

    # ------------------------------------------------------------------
    # キーワードマッチング
    # ------------------------------------------------------------------

    def _match_keyword(self, label: str) -> Optional[str]:
        """科目ラベルを内部フィールド名に変換する"""
        label = label.strip()
        # 完全一致
        if label in _KEYWORD_MAP:
            return _KEYWORD_MAP[label]
        # 部分一致（長いキーワードを優先）
        for kw in sorted(_KEYWORD_MAP.keys(), key=len, reverse=True):
            if kw in label:
                return _KEYWORD_MAP[kw]
        return None

    # ------------------------------------------------------------------
    # 期間推測
    # ------------------------------------------------------------------

    def _guess_period(self, text: str) -> str:
        """テキストから会計期間文字列を推測する"""
        # 「2024年3月期」のような表記を探す
        m = re.search(r"(\d{4}年\d{1,2}月期)", text)
        if m:
            return m.group(1)
        m = re.search(r"(令和\d+年\d{1,2}月期)", text)
        if m:
            return m.group(1)
        m = re.search(r"(第\d+期)", text)
        if m:
            return m.group(1)
        return ""

    # ------------------------------------------------------------------
    # IncomeStatement 組み立て
    # ------------------------------------------------------------------

    def _build_income_statement(
        self, fields: Dict[str, float], period: str
    ) -> IncomeStatement:
        """抽出フィールドから IncomeStatement を組み立てる"""
        # 販管費が合算の場合は半分ずつ割り当て（概算）
        if "selling_and_admin" in fields and "selling_expenses" not in fields:
            combined = fields.pop("selling_and_admin")
            fields["selling_expenses"] = combined * 0.5
            fields["general_admin_expenses"] = combined * 0.5
        elif "selling_and_admin" in fields:
            fields.pop("selling_and_admin", None)

        def get(key: str, default: float = 0.0) -> float:
            return fields.get(key, default)

        # 提供値があるフィールドは明示的に渡し、自動計算に任せる
        kwargs: Dict = dict(
            period=period,
            revenue=get("revenue"),
            cost_of_goods_sold=get("cost_of_goods_sold"),
            selling_expenses=get("selling_expenses"),
            general_admin_expenses=get("general_admin_expenses"),
            non_operating_income=get("non_operating_income"),
            non_operating_expenses=get("non_operating_expenses"),
            extraordinary_income=get("extraordinary_income"),
            extraordinary_losses=get("extraordinary_losses"),
            income_tax=get("income_tax"),
        )

        # PDF に利益行が直接記載されている場合は上書き
        for key in ("gross_profit", "operating_income", "ordinary_income",
                    "income_before_tax", "net_income"):
            if key in fields:
                kwargs[key] = fields[key]

        return IncomeStatement(**kwargs)
