"""
財務レポート生成モジュール

分析結果を人間が読みやすいテキスト／Markdownレポートとして出力します。
"""

from .analyzer import AnalysisResult


class ReportGenerator:
    """財務分析結果をレポート形式で出力するクラス"""

    def generate_text(self, result: AnalysisResult) -> str:
        """プレーンテキスト形式のレポートを生成する"""
        lines = []
        sep = "=" * 60

        lines.append(sep)
        lines.append(f"  財務分析レポート: {result.company_name}")
        lines.append(f"  対象期間: {result.period}")
        lines.append(sep)

        lines.append(f"\n総合評価スコア: {result.overall_score:.1f} / 100")
        for c in result.overall_comments:
            lines.append(f"  → {c}")

        # 収益性
        lines.append("\n" + "-" * 40)
        lines.append("【収益性指標】")
        p = result.profitability
        lines.append(f"  売上総利益率:   {p.gross_profit_margin:7.2f} %")
        lines.append(f"  営業利益率:     {p.operating_profit_margin:7.2f} %")
        lines.append(f"  純利益率:       {p.net_profit_margin:7.2f} %")
        lines.append(f"  ROA:            {p.return_on_assets:7.2f} %")
        lines.append(f"  ROE:            {p.return_on_equity:7.2f} %")
        if p.ebitda_margin is not None:
            lines.append(f"  EBITDAマージン: {p.ebitda_margin:7.2f} %")
        lines.append("  評価:")
        for c in result.profitability_comments:
            lines.append(f"    ・{c}")

        # 安全性
        lines.append("\n" + "-" * 40)
        lines.append("【安全性指標】")
        s = result.safety
        lines.append(f"  流動比率:         {s.current_ratio:7.2f} %")
        lines.append(f"  当座比率:         {s.quick_ratio:7.2f} %")
        lines.append(f"  負債資本比率:     {s.debt_to_equity_ratio:7.2f} 倍")
        lines.append(f"  自己資本比率:     {s.equity_ratio:7.2f} %")
        if s.interest_coverage_ratio is not None:
            lines.append(f"  IC レシオ:        {s.interest_coverage_ratio:7.2f} 倍")
        lines.append("  評価:")
        for c in result.safety_comments:
            lines.append(f"    ・{c}")

        # 効率性
        lines.append("\n" + "-" * 40)
        lines.append("【効率性指標】")
        e = result.efficiency
        lines.append(f"  総資産回転率:     {e.asset_turnover:7.2f} 回")
        if e.inventory_turnover is not None:
            lines.append(f"  棚卸資産回転率:   {e.inventory_turnover:7.2f} 回")
        if e.receivables_turnover is not None:
            lines.append(f"  売掛金回転率:     {e.receivables_turnover:7.2f} 回")
        if e.days_sales_outstanding is not None:
            lines.append(f"  売掛金回収日数:   {e.days_sales_outstanding:7.1f} 日")
        if e.days_inventory_outstanding is not None:
            lines.append(f"  棚卸資産回転日数: {e.days_inventory_outstanding:7.1f} 日")
        lines.append("  評価:")
        for c in result.efficiency_comments:
            lines.append(f"    ・{c}")

        # 成長性
        lines.append("\n" + "-" * 40)
        lines.append("【成長性指標】")
        g = result.growth
        if g.revenue_growth_rate is not None:
            lines.append(f"  売上高成長率:     {g.revenue_growth_rate:+7.2f} %")
        if g.operating_income_growth_rate is not None:
            lines.append(f"  営業利益成長率:   {g.operating_income_growth_rate:+7.2f} %")
        if g.net_income_growth_rate is not None:
            lines.append(f"  純利益成長率:     {g.net_income_growth_rate:+7.2f} %")
        if g.total_assets_growth_rate is not None:
            lines.append(f"  総資産成長率:     {g.total_assets_growth_rate:+7.2f} %")
        lines.append("  評価:")
        for c in result.growth_comments:
            lines.append(f"    ・{c}")

        # キャッシュフロー
        lines.append("\n" + "-" * 40)
        lines.append("【キャッシュフロー指標】")
        cf = result.cash_flow
        lines.append(f"  営業CFマージン:   {cf.operating_cf_margin:7.2f} %")
        lines.append(f"  フリーCF:         {cf.free_cash_flow:>14,.0f} 円")
        if cf.cash_flow_to_debt is not None:
            lines.append(f"  CF / 有利子負債:  {cf.cash_flow_to_debt:7.2f} 倍")
        lines.append("  評価:")
        for c in result.cash_flow_comments:
            lines.append(f"    ・{c}")

        lines.append("\n" + sep)

        return "\n".join(lines)

    def generate_markdown(self, result: AnalysisResult) -> str:
        """Markdown形式のレポートを生成する"""
        lines = []

        lines.append(f"# 財務分析レポート: {result.company_name}")
        lines.append(f"\n**対象期間:** {result.period}\n")
        lines.append(f"## 総合評価スコア: {result.overall_score:.1f} / 100\n")
        for c in result.overall_comments:
            lines.append(f"> {c}\n")

        # 収益性
        lines.append("## 収益性指標\n")
        p = result.profitability
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 売上総利益率 | {p.gross_profit_margin:.2f}% |")
        lines.append(f"| 営業利益率 | {p.operating_profit_margin:.2f}% |")
        lines.append(f"| 純利益率 | {p.net_profit_margin:.2f}% |")
        lines.append(f"| ROA | {p.return_on_assets:.2f}% |")
        lines.append(f"| ROE | {p.return_on_equity:.2f}% |")
        if p.ebitda_margin is not None:
            lines.append(f"| EBITDAマージン | {p.ebitda_margin:.2f}% |")
        lines.append("")
        for c in result.profitability_comments:
            lines.append(f"- {c}")
        lines.append("")

        # 安全性
        lines.append("## 安全性指標\n")
        s = result.safety
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 流動比率 | {s.current_ratio:.2f}% |")
        lines.append(f"| 当座比率 | {s.quick_ratio:.2f}% |")
        lines.append(f"| 負債資本比率 | {s.debt_to_equity_ratio:.2f}倍 |")
        lines.append(f"| 自己資本比率 | {s.equity_ratio:.2f}% |")
        if s.interest_coverage_ratio is not None:
            lines.append(f"| ICレシオ | {s.interest_coverage_ratio:.2f}倍 |")
        lines.append("")
        for c in result.safety_comments:
            lines.append(f"- {c}")
        lines.append("")

        # 効率性
        lines.append("## 効率性指標\n")
        e = result.efficiency
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 総資産回転率 | {e.asset_turnover:.2f}回 |")
        if e.inventory_turnover is not None:
            lines.append(f"| 棚卸資産回転率 | {e.inventory_turnover:.2f}回 |")
        if e.receivables_turnover is not None:
            lines.append(f"| 売掛金回転率 | {e.receivables_turnover:.2f}回 |")
        if e.days_sales_outstanding is not None:
            lines.append(f"| 売掛金回収日数 | {e.days_sales_outstanding:.1f}日 |")
        if e.days_inventory_outstanding is not None:
            lines.append(f"| 棚卸資産回転日数 | {e.days_inventory_outstanding:.1f}日 |")
        lines.append("")
        for c in result.efficiency_comments:
            lines.append(f"- {c}")
        lines.append("")

        # 成長性
        lines.append("## 成長性指標\n")
        g = result.growth
        if g.revenue_growth_rate is not None:
            lines.append("| 指標 | 値 |")
            lines.append("|------|-----|")
            lines.append(f"| 売上高成長率 | {g.revenue_growth_rate:+.2f}% |")
            if g.operating_income_growth_rate is not None:
                lines.append(f"| 営業利益成長率 | {g.operating_income_growth_rate:+.2f}% |")
            if g.net_income_growth_rate is not None:
                lines.append(f"| 純利益成長率 | {g.net_income_growth_rate:+.2f}% |")
            if g.total_assets_growth_rate is not None:
                lines.append(f"| 総資産成長率 | {g.total_assets_growth_rate:+.2f}% |")
            lines.append("")
        for c in result.growth_comments:
            lines.append(f"- {c}")
        lines.append("")

        # キャッシュフロー
        lines.append("## キャッシュフロー指標\n")
        cf = result.cash_flow
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 営業CFマージン | {cf.operating_cf_margin:.2f}% |")
        lines.append(f"| フリーキャッシュフロー | {cf.free_cash_flow:,.0f}円 |")
        if cf.cash_flow_to_debt is not None:
            lines.append(f"| CF/有利子負債 | {cf.cash_flow_to_debt:.2f}倍 |")
        lines.append("")
        for c in result.cash_flow_comments:
            lines.append(f"- {c}")

        return "\n".join(lines)
