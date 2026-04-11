"""
財務分析ツール 実行スクリプト

使い方:
  # サンプルデータで実行
  python examples/run_analysis.py

  # PDFファイルを指定して実行
  python examples/run_analysis.py --pdf 決算書.pdf

  # 企業名・期間・金額単位を指定
  python examples/run_analysis.py --pdf 決算書.pdf --company "株式会社〇〇" --period "2024年3月期" --unit 1000

  # Markdown形式でファイルに保存
  python examples/run_analysis.py --pdf 決算書.pdf --format markdown --output report.md

  # PDFから抽出したテキストをデバッグ表示（抽出がうまくいかない場合に使用）
  python examples/run_analysis.py --pdf 決算書.pdf --debug
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analysis import FinancialAnalyzer, ReportGenerator, PdfIncomeStatementLoader
from examples.sample_data import sample_financial_data


def main():
    parser = argparse.ArgumentParser(
        description="財務分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pdf",
        metavar="FILE",
        help="分析するPDFファイルのパス（省略時はサンプルデータを使用）",
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
        help="金額単位の倍率（千円単位なら1000、百万円単位なら1000000）",
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
        help="PDFから抽出した生テキストを表示（抽出確認用）",
    )
    args = parser.parse_args()

    analyzer = FinancialAnalyzer()
    generator = ReportGenerator()

    # --- データ読み込み ---
    if args.pdf:
        loader = PdfIncomeStatementLoader()

        if args.debug:
            print("=== PDFから抽出したテキスト（デバッグ） ===")
            print(loader.extract_text_for_debug(args.pdf))
            print("=" * 60)
            return

        print(f"PDFを読み込み中: {args.pdf}")
        try:
            data = loader.load(
                args.pdf,
                company_name=args.company,
                period=args.period,
                unit=args.unit,
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)

        # 読み込んだ主要数値を表示
        is_ = data.income_statement
        print(f"\n--- 抽出した主要数値 ({data.company_name} / {is_.period}) ---")
        print(f"  売上高:     {is_.revenue:>15,.0f}")
        print(f"  売上原価:   {is_.cost_of_goods_sold:>15,.0f}")
        print(f"  売上総利益: {is_.gross_profit:>15,.0f}")
        print(f"  営業利益:   {is_.operating_income:>15,.0f}")
        print(f"  当期純利益: {is_.net_income:>15,.0f}")
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
