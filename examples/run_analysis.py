"""
財務分析ツール 実行スクリプト

対応ファイル形式: PDF / Excel (.xlsx/.xls) / Word (.docx)

使い方:
  # サンプルデータで実行
  python examples/run_analysis.py

  # ファイルを指定して実行（形式は拡張子で自動判定）
  python examples/run_analysis.py --input 決算書.pdf
  python examples/run_analysis.py --input 月次PL.xlsx
  python examples/run_analysis.py --input 報告書.docx

  # オプション指定
  python examples/run_analysis.py --input 月次PL.xlsx \\
      --company "株式会社〇〇" \\
      --period "2024年3月期" \\
      --unit 1000            # 千円単位の場合

  # Excelのシート名を指定
  python examples/run_analysis.py --input 月次PL.xlsx --sheet "損益計算書"

  # Markdownで出力
  python examples/run_analysis.py --input 決算書.pdf --format markdown --output report.md

  # 抽出内容をデバッグ確認
  python examples/run_analysis.py --input 決算書.pdf --debug
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analysis import FinancialAnalyzer, ReportGenerator, load_financial_data, extract_debug_text
from examples.sample_data import sample_financial_data

_SUPPORTED = ".pdf, .xlsx, .xls, .docx"


def main():
    parser = argparse.ArgumentParser(
        description="財務分析ツール（PDF / Excel / Word 対応）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help=f"分析するファイルのパス（対応形式: {_SUPPORTED}）",
    )
    parser.add_argument(
        "--company",
        metavar="NAME",
        default="",
        help="企業名（省略時はファイル名）",
    )
    parser.add_argument(
        "--period",
        metavar="PERIOD",
        default="",
        help='会計期間（例: "2024年3月期"）',
    )
    parser.add_argument(
        "--unit",
        metavar="MULTIPLIER",
        type=float,
        default=1.0,
        help="金額単位の倍率（千円単位=1000, 百万円単位=1000000）",
    )
    parser.add_argument(
        "--sheet",
        metavar="SHEET_NAME",
        default=None,
        help="Excelのシート名（省略時は自動選択）",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="出力フォーマット（デフォルト: text）",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="出力ファイルパス（省略時は標準出力）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="ファイルから抽出したテキスト・表データを表示（抽出確認用）",
    )
    args = parser.parse_args()

    analyzer = FinancialAnalyzer()
    generator = ReportGenerator()

    # --- デバッグモード ---
    if args.debug:
        if not args.input:
            print("--debug には --input でファイルを指定してください。", file=sys.stderr)
            sys.exit(1)
        try:
            print(extract_debug_text(args.input, sheet_name=args.sheet))
        except Exception as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # --- データ読み込み ---
    if args.input:
        print(f"ファイルを読み込み中: {args.input}")
        try:
            data = load_financial_data(
                args.input,
                company_name=args.company,
                period=args.period,
                unit=args.unit,
                sheet_name=args.sheet,
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)

        # 読み込んだ主要数値を表示
        is_ = data.income_statement
        print(f"\n--- 抽出した主要数値 ({data.company_name} / {is_.period or '期間不明'}) ---")
        items = [
            ("売上高",     is_.revenue),
            ("売上原価",   is_.cost_of_goods_sold),
            ("売上総利益", is_.gross_profit),
            ("営業利益",   is_.operating_income),
            ("当期純利益", is_.net_income),
        ]
        for label, val in items:
            mark = "  " if val else "※"
            print(f"  {mark}{label:8s}: {val:>15,.0f}")
        if not is_.revenue:
            print("\n  ※ 売上高が0です。--debug でファイルの抽出内容を確認してください。")
        print()

    else:
        data = sample_financial_data

    # --- 分析・レポート生成 ---
    result = analyzer.analyze(data)

    if args.format == "markdown":
        report = generator.generate_markdown(result)
    else:
        report = generator.generate_text(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"レポートを {args.output} に出力しました。")
    else:
        print(report)


if __name__ == "__main__":
    main()
