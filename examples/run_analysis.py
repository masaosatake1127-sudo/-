"""
財務分析ツール 実行例

使い方:
  python examples/run_analysis.py
  python examples/run_analysis.py --format markdown
  python examples/run_analysis.py --format markdown --output report.md
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analysis import FinancialAnalyzer, ReportGenerator
from examples.sample_data import sample_financial_data


def main():
    parser = argparse.ArgumentParser(description="財務分析ツール")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="出力フォーマット (デフォルト: text)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="出力ファイルパス（省略時は標準出力）",
    )
    args = parser.parse_args()

    analyzer = FinancialAnalyzer()
    generator = ReportGenerator()

    result = analyzer.analyze(sample_financial_data)

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
