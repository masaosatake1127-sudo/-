"""
統合ファイルローダー

拡張子からファイル形式を自動判定し、適切なローダーに振り分けます。

対応形式:
  .pdf              → PdfIncomeStatementLoader
  .xlsx / .xls      → ExcelIncomeStatementLoader
  .docx             → WordIncomeStatementLoader

使い方:
    from financial_analysis.file_loader import load_financial_data

    data = load_financial_data("決算書.pdf", company_name="株式会社〇〇")
    data = load_financial_data("月次PL.xlsx", unit=1000)
    data = load_financial_data("報告書.docx")
"""

from pathlib import Path
from typing import Optional

from .models import FinancialData
from .pdf_loader import PdfIncomeStatementLoader
from .excel_loader import ExcelIncomeStatementLoader
from .word_loader import WordIncomeStatementLoader


_PDF_EXTENSIONS = {".pdf"}
_EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
_WORD_EXTENSIONS = {".docx", ".doc"}


def load_financial_data(
    file_path: str,
    company_name: str = "",
    period: str = "",
    unit: float = 1.0,
    sheet_name: Optional[str] = None,
) -> FinancialData:
    """
    ファイル形式を自動判定して財務データを読み込む。

    Args:
        file_path:    対応ファイルのパス（PDF / Excel / Word）
        company_name: 企業名（省略時はファイル名）
        period:       会計期間文字列（例: "2024年3月期"）
        unit:         金額単位の倍率（千円=1000, 百万円=1000000）
        sheet_name:   Excelのシート名（省略時は自動選択）

    Returns:
        FinancialData

    Raises:
        ValueError: 非対応の拡張子の場合
        FileNotFoundError: ファイルが存在しない場合
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in _PDF_EXTENSIONS:
        loader = PdfIncomeStatementLoader()
        return loader.load(file_path, company_name=company_name, period=period, unit=unit)

    if ext in _EXCEL_EXTENSIONS:
        loader = ExcelIncomeStatementLoader()
        return loader.load(
            file_path,
            company_name=company_name,
            period=period,
            sheet_name=sheet_name,
            unit=unit,
        )

    if ext in _WORD_EXTENSIONS:
        loader = WordIncomeStatementLoader()
        return loader.load(file_path, company_name=company_name, period=period, unit=unit)

    supported = ", ".join(
        sorted(_PDF_EXTENSIONS | _EXCEL_EXTENSIONS | _WORD_EXTENSIONS)
    )
    raise ValueError(
        f"非対応のファイル形式です: {ext}\n"
        f"対応形式: {supported}"
    )


def extract_debug_text(file_path: str, sheet_name: Optional[str] = None) -> str:
    """
    デバッグ用: ファイルから抽出した生テキストを返す。

    Args:
        file_path:  対応ファイルのパス
        sheet_name: Excelのシート名（省略時は自動選択）
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in _PDF_EXTENSIONS:
        return PdfIncomeStatementLoader().extract_text_for_debug(file_path)

    if ext in _EXCEL_EXTENSIONS:
        return ExcelIncomeStatementLoader().extract_rows_for_debug(file_path, sheet_name)

    if ext in _WORD_EXTENSIONS:
        return WordIncomeStatementLoader().extract_text_for_debug(file_path)

    raise ValueError(f"非対応のファイル形式です: {ext}")
