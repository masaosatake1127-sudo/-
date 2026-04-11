"""
Excelファイル財務データローダー

.xlsx / .xls 形式の月別損益計算書を読み込み、FinancialData に変換します。

対応フォーマット:
  [パターンA] 科目が行、月が列（最も一般的）
       A        B        C    ...   N      O
  1  勘定科目   4月      5月  ...  3月    合計
  2  売上高     100      110  ...  120   1230
  ...

  [パターンB] 月が行、科目が列
       A     B       C      ...
  1   月    売上高   売上原価 ...
  2   4月   100     40     ...
  ...

使い方:
    loader = ExcelIncomeStatementLoader()
    data = loader.load("月次PL.xlsx", company_name="株式会社〇〇")
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import openpyxl
from openpyxl.utils import get_column_letter

from .models import BalanceSheet, CashFlowStatement, FinancialData, IncomeStatement
from .pdf_loader import _KEYWORD_MAP, _parse_number


class ExcelIncomeStatementLoader:
    """
    Excel ファイルから月別損益計算書を読み込み FinancialData を返すローダー。
    """

    def load(
        self,
        file_path: str,
        company_name: str = "",
        period: str = "",
        sheet_name: Optional[str] = None,
        unit: float = 1.0,
    ) -> FinancialData:
        """
        Excel ファイルを読み込んで FinancialData を返す。

        Args:
            file_path:   Excel ファイルのパス (.xlsx / .xls)
            company_name: 企業名（省略時はファイル名）
            period:      会計期間（例: "2024年3月期"）
            sheet_name:  読み込むシート名（省略時は最初のシート）
            unit:        金額単位の倍率（千円=1000, 百万円=1000000）
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        if path.suffix.lower() not in (".xlsx", ".xls", ".xlsm"):
            raise ValueError(f"Excelファイル (.xlsx/.xls) を指定してください: {file_path}")

        if not company_name:
            company_name = path.stem

        rows, sheet_title = self._read_sheet(str(path), sheet_name)
        fields = self._parse_rows(rows, unit)

        if not fields:
            raise ValueError(
                f"Excelファイルから財務データを抽出できませんでした。\n"
                f"シート: {sheet_title}\n"
                f"・勘定科目名（売上高・売上原価・営業利益など）が含まれているか確認してください\n"
                f"・--debug オプションで抽出内容を確認できます"
            )

        if not period:
            period = self._guess_period_from_rows(rows)

        income_stmt = self._build_income_statement(fields, period)
        balance_sheet = BalanceSheet()
        cash_flow = CashFlowStatement(net_income=income_stmt.net_income or 0.0)

        return FinancialData(
            company_name=company_name,
            income_statement=income_stmt,
            balance_sheet=balance_sheet,
            cash_flow_statement=cash_flow,
        )

    def extract_rows_for_debug(self, file_path: str, sheet_name: Optional[str] = None) -> str:
        """デバッグ用: シートの全セル内容を文字列で返す"""
        rows, sheet_title = self._read_sheet(file_path, sheet_name)
        lines = [f"シート: {sheet_title}", ""]
        for ri, row in enumerate(rows):
            cells = "\t".join(str(c) for c in row)
            lines.append(f"行{ri+1:3d}: {cells}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # シート読み込み
    # ------------------------------------------------------------------

    def _read_sheet(
        self, file_path: str, sheet_name: Optional[str]
    ) -> Tuple[List[List[Any]], str]:
        """openpyxl でシートを読み込み、2次元リストを返す"""
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)

        if sheet_name:
            if sheet_name not in wb.sheetnames:
                raise ValueError(
                    f"シート '{sheet_name}' が見つかりません。"
                    f"存在するシート: {wb.sheetnames}"
                )
            ws = wb[sheet_name]
        else:
            # 損益計算書っぽいシートを優先して選択
            ws = self._find_pl_sheet(wb)

        title = ws.title
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append(list(row))
        wb.close()
        return rows, title

    def _find_pl_sheet(self, wb):
        """損益計算書らしいシートを探す（なければ先頭シート）"""
        pl_keywords = ("損益", "PL", "P&L", "pl", "収益", "売上", "income")
        for name in wb.sheetnames:
            if any(kw in name for kw in pl_keywords):
                return wb[name]
        return wb[wb.sheetnames[0]]

    # ------------------------------------------------------------------
    # パース
    # ------------------------------------------------------------------

    def _parse_rows(self, rows: List[List[Any]], unit: float) -> Dict[str, float]:
        """行データから勘定科目と金額を抽出する"""
        if not rows:
            return {}

        # ヘッダー行を探す（月名または勘定科目名が含まれる行）
        header_row_idx, header = self._find_header_row(rows)

        # パターンA: 科目が行、月/合計が列
        total_col = self._find_total_column(header)
        if total_col is not None:
            return self._parse_pattern_a(rows, header_row_idx, total_col, unit)

        # パターンB: 月が行、科目が列
        col_fields = self._map_column_fields(header)
        if col_fields:
            return self._parse_pattern_b(rows, header_row_idx, col_fields, unit)

        # どちらでもない: 全行をスキャンして科目+数値ペアを探す
        return self._parse_any(rows, unit)

    def _find_header_row(self, rows: List[List[Any]]) -> Tuple[int, List[str]]:
        """ヘッダー行のインデックスと内容を返す"""
        import re
        month_re = re.compile(r"\d{1,2}月")
        for i, row in enumerate(rows[:20]):  # 先頭20行を探索
            strs = [str(c or "").strip() for c in row]
            # 月名が3つ以上あるか、勘定科目キーワードが含まれるか
            if sum(1 for s in strs if month_re.search(s)) >= 3:
                return i, strs
            if any(kw in " ".join(strs) for kw in ("合計", "売上高", "勘定科目")):
                return i, strs
        return 0, [str(c or "").strip() for c in rows[0]]

    def _find_total_column(self, header: List[str]) -> Optional[int]:
        """合計列のインデックスを返す"""
        import re
        month_re = re.compile(r"\d{1,2}月")
        for i, h in enumerate(header):
            if any(k in h for k in ("合計", "累計", "年計", "通期", "決算")):
                return i
        # 月列が並んでいれば最後を合計とみなす
        month_cols = [i for i, h in enumerate(header) if month_re.search(h)]
        if len(month_cols) >= 3:
            return max(month_cols)
        return None

    def _map_column_fields(self, header: List[str]) -> Dict[int, str]:
        """ヘッダーの各列を内部フィールド名にマッピングする"""
        result = {}
        for i, h in enumerate(header):
            field = self._match_keyword(h)
            if field:
                result[i] = field
        return result

    def _parse_pattern_a(
        self,
        rows: List[List[Any]],
        header_idx: int,
        total_col: int,
        unit: float,
    ) -> Dict[str, float]:
        """科目が行、月/合計が列のパターン"""
        fields: Dict[str, float] = {}
        for row in rows[header_idx + 1 :]:
            if not row:
                continue
            label = str(row[0] or "").strip()
            field = self._match_keyword(label)
            if field and total_col < len(row):
                val = _parse_number(str(row[total_col] if row[total_col] is not None else ""))
                if val is not None:
                    fields.setdefault(field, val * unit)
        return fields

    def _parse_pattern_b(
        self,
        rows: List[List[Any]],
        header_idx: int,
        col_fields: Dict[int, str],
        unit: float,
    ) -> Dict[str, float]:
        """月が行、科目が列のパターン（月ごとに合算）"""
        totals: Dict[str, float] = {}
        for row in rows[header_idx + 1 :]:
            if not row:
                continue
            label = str(row[0] or "").strip()
            is_total = any(k in label for k in ("合計", "累計", "年計"))
            for ci, f in col_fields.items():
                if ci < len(row) and row[ci] is not None:
                    val = _parse_number(str(row[ci]))
                    if val is not None:
                        if is_total:
                            totals[f] = val * unit
                        else:
                            totals[f] = totals.get(f, 0.0) + val * unit
        return totals

    def _parse_any(self, rows: List[List[Any]], unit: float) -> Dict[str, float]:
        """科目+数値を総当たりでスキャンする"""
        fields: Dict[str, float] = {}
        for row in rows:
            if not row:
                continue
            label = str(row[0] or "").strip()
            field = self._match_keyword(label)
            if field:
                # 行の中で最後の数値を金額とみなす
                for cell in reversed(row[1:]):
                    val = _parse_number(str(cell if cell is not None else ""))
                    if val is not None:
                        fields.setdefault(field, val * unit)
                        break
        return fields

    # ------------------------------------------------------------------
    # 期間推測
    # ------------------------------------------------------------------

    def _guess_period_from_rows(self, rows: List[List[Any]]) -> str:
        """セル内容から会計期間文字列を推測する"""
        import re
        for row in rows[:10]:
            for cell in row:
                text = str(cell or "")
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
        """科目ラベルを内部フィールド名に変換する"""
        label = label.strip()
        if label in _KEYWORD_MAP:
            return _KEYWORD_MAP[label]
        for kw in sorted(_KEYWORD_MAP.keys(), key=len, reverse=True):
            if kw in label:
                return _KEYWORD_MAP[kw]
        return None

    # ------------------------------------------------------------------
    # IncomeStatement 組み立て（pdf_loader と共通ロジック）
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
