"""
Wordファイル財務データローダー

.docx 形式の損益計算書を読み込み、FinancialData に変換します。

対応フォーマット:
  - Word文書内の表（Table）に含まれる損益計算書
  - 本文テキストに「売上高 50,000,000」のように記載されたもの

  [表のイメージ]
  ┌──────────┬──────────┬──────────┬──────────┐
  │ 勘定科目   │   4月    │  5月     │   合計   │
  ├──────────┼──────────┼──────────┼──────────┤
  │ 売上高     │1,000,000 │1,100,000 │50,000,000│
  │ 売上原価   │  400,000 │  440,000 │20,000,000│
  ...

使い方:
    loader = WordIncomeStatementLoader()
    data = loader.load("月次PL.docx", company_name="株式会社〇〇")
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import docx

from .models import BalanceSheet, CashFlowStatement, FinancialData, IncomeStatement
from .pdf_loader import _KEYWORD_MAP, _parse_number


class WordIncomeStatementLoader:
    """
    Word(.docx)ファイルから損益計算書を読み込み FinancialData を返すローダー。
    """

    def load(
        self,
        file_path: str,
        company_name: str = "",
        period: str = "",
        unit: float = 1.0,
    ) -> FinancialData:
        """
        Word ファイルを読み込んで FinancialData を返す。

        Args:
            file_path:    Word ファイルのパス (.docx)
            company_name: 企業名（省略時はファイル名）
            period:       会計期間（例: "2024年3月期"）
            unit:         金額単位の倍率（千円=1000, 百万円=1000000）
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        if path.suffix.lower() not in (".docx", ".doc"):
            raise ValueError(f"Wordファイル (.docx) を指定してください: {file_path}")
        if path.suffix.lower() == ".doc":
            raise ValueError(
                ".doc 形式は非対応です。Word で「名前を付けて保存」→「.docx」に変換してください。"
            )

        if not company_name:
            company_name = path.stem

        doc = docx.Document(str(path))

        # 期間を本文から推測
        if not period:
            period = self._guess_period(doc)

        # 表から抽出を優先
        fields = self._parse_tables(doc, unit)

        # 表がなければ本文テキストから抽出
        if not fields:
            fields = self._parse_paragraphs(doc, unit)

        if not fields:
            raise ValueError(
                "Wordファイルから財務データを抽出できませんでした。\n"
                "・文書内に表（Table）形式で損益計算書が記載されているか確認してください\n"
                "・--debug オプションで抽出内容を確認できます"
            )

        income_stmt = self._build_income_statement(fields, period)
        balance_sheet = BalanceSheet()
        cash_flow = CashFlowStatement(net_income=income_stmt.net_income or 0.0)

        return FinancialData(
            company_name=company_name,
            income_statement=income_stmt,
            balance_sheet=balance_sheet,
            cash_flow_statement=cash_flow,
        )

    def extract_text_for_debug(self, file_path: str) -> str:
        """デバッグ用: 文書内のテキストと表の内容を返す"""
        doc = docx.Document(file_path)
        lines = ["=== 本文テキスト ==="]
        for para in doc.paragraphs:
            if para.text.strip():
                lines.append(para.text)

        lines.append("\n=== 表データ ===")
        for ti, table in enumerate(doc.tables):
            lines.append(f"\n--- 表 {ti + 1} ---")
            for row in table.rows:
                cells = " | ".join(c.text.strip() for c in row.cells)
                lines.append(cells)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 表からの抽出
    # ------------------------------------------------------------------

    def _parse_tables(self, doc, unit: float) -> Dict[str, float]:
        """文書内の全表を走査して財務フィールドを抽出する"""
        fields: Dict[str, float] = {}

        for table in doc.tables:
            rows = [[c.text.strip() for c in row.cells] for row in table.rows]
            if not rows:
                continue

            table_fields = self._parse_table_rows(rows, unit)
            # 多くの科目を含む表を優先
            if len(table_fields) > len(fields):
                fields = table_fields

        return fields

    def _parse_table_rows(self, rows: List[List[str]], unit: float) -> Dict[str, float]:
        """表の行リストから財務フィールドを抽出する"""
        if not rows:
            return {}

        header = rows[0]

        # パターンA: 科目が行、月/合計が列
        total_col = self._find_total_column(header)
        if total_col is not None:
            fields: Dict[str, float] = {}
            for row in rows[1:]:
                if not row:
                    continue
                label = row[0]
                field = self._match_keyword(label)
                if field and total_col < len(row):
                    val = _parse_number(row[total_col])
                    if val is not None:
                        fields.setdefault(field, val * unit)
            return fields

        # パターンB: 月が行、科目が列
        col_fields = {}
        for ci, h in enumerate(header):
            f = self._match_keyword(h)
            if f:
                col_fields[ci] = f

        if col_fields:
            totals: Dict[str, float] = {}
            for row in rows[1:]:
                label = row[0] if row else ""
                is_total = any(k in label for k in ("合計", "累計", "年計"))
                for ci, f in col_fields.items():
                    if ci < len(row):
                        val = _parse_number(row[ci])
                        if val is not None:
                            if is_total:
                                totals[f] = val * unit
                            else:
                                totals[f] = totals.get(f, 0.0) + val * unit
            return totals

        # パターンC: 科目+数値の2列形式
        fields = {}
        for row in rows:
            if len(row) < 2:
                continue
            label = row[0]
            field = self._match_keyword(label)
            if field:
                # 最後の列の数値を採用
                for cell in reversed(row[1:]):
                    val = _parse_number(cell)
                    if val is not None:
                        fields.setdefault(field, val * unit)
                        break
        return fields

    def _find_total_column(self, header: List[str]) -> Optional[int]:
        """合計列のインデックスを返す"""
        month_re = re.compile(r"\d{1,2}月")
        for i, h in enumerate(header):
            if any(k in h for k in ("合計", "累計", "年計", "通期", "決算")):
                return i
        month_cols = [i for i, h in enumerate(header) if month_re.search(h)]
        if len(month_cols) >= 3:
            return max(month_cols)
        return None

    # ------------------------------------------------------------------
    # 本文テキストからの抽出（表がない場合のフォールバック）
    # ------------------------------------------------------------------

    def _parse_paragraphs(self, doc, unit: float) -> Dict[str, float]:
        """段落テキストから科目名+金額のペアを抽出する"""
        fields: Dict[str, float] = {}
        number_re = re.compile(
            r"([△▲▽(（]?\s*[\d,，]+\s*[)）]?)"
        )
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            field = self._match_keyword(text.split()[0] if text.split() else text)
            if field:
                nums = number_re.findall(text)
                if nums:
                    val = _parse_number(nums[-1])
                    if val is not None:
                        fields.setdefault(field, val * unit)
        return fields

    # ------------------------------------------------------------------
    # 期間推測
    # ------------------------------------------------------------------

    def _guess_period(self, doc) -> str:
        """文書本文から会計期間文字列を推測する"""
        text = "\n".join(p.text for p in doc.paragraphs[:20])
        for table in doc.tables[:2]:
            for row in table.rows[:3]:
                text += " " + " ".join(c.text for c in row.cells)

        m = re.search(r"(\d{4}年\d{1,2}月期)", text)
        if m:
            return m.group(1)
        m = re.search(r"(令和\d+年\d{1,2}月期)", text)
        if m:
            return m.group(1)
        return ""

    # ------------------------------------------------------------------
    # キーワードマッチング
    # ------------------------------------------------------------------

    def _match_keyword(self, label: str) -> Optional[str]:
        label = label.strip()
        if label in _KEYWORD_MAP:
            return _KEYWORD_MAP[label]
        for kw in sorted(_KEYWORD_MAP.keys(), key=len, reverse=True):
            if kw in label:
                return _KEYWORD_MAP[kw]
        return None

    # ------------------------------------------------------------------
    # IncomeStatement 組み立て
    # ------------------------------------------------------------------

    def _build_income_statement(
        self, fields: Dict[str, float], period: str
    ) -> IncomeStatement:
        if "selling_and_admin" in fields and "selling_expenses" not in fields:
            combined = fields.pop("selling_and_admin")
            fields["selling_expenses"] = combined * 0.5
            fields["general_admin_expenses"] = combined * 0.5
        else:
            fields.pop("selling_and_admin", None)

        def get(key: str) -> float:
            return fields.get(key, 0.0)

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
        for key in ("gross_profit", "operating_income", "ordinary_income",
                    "income_before_tax", "net_income"):
            if key in fields:
                kwargs[key] = fields[key]

        return IncomeStatement(**kwargs)
