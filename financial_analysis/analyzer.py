"""
財務分析エンジン

財務諸表から各種指標を計算し、評価・コメントを付与します。
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .models import FinancialData
from .ratios import (
    FinancialRatios,
    ProfitabilityRatios,
    SafetyRatios,
    EfficiencyRatios,
    GrowthRatios,
    CashFlowRatios,
)


@dataclass
class AnalysisResult:
    """財務分析結果"""
    company_name: str
    period: str

    profitability: ProfitabilityRatios
    safety: SafetyRatios
    efficiency: EfficiencyRatios
    growth: GrowthRatios
    cash_flow: CashFlowRatios

    profitability_comments: List[str] = field(default_factory=list)
    safety_comments: List[str] = field(default_factory=list)
    efficiency_comments: List[str] = field(default_factory=list)
    growth_comments: List[str] = field(default_factory=list)
    cash_flow_comments: List[str] = field(default_factory=list)

    overall_score: Optional[float] = None
    overall_comments: List[str] = field(default_factory=list)


class FinancialAnalyzer:
    """財務データを分析し評価コメントを生成するアナライザー"""

    def analyze(self, data: FinancialData) -> AnalysisResult:
        """財務データを分析してAnalysisResultを返す"""
        ratios = FinancialRatios(
            income_stmt=data.income_statement,
            balance_sheet=data.balance_sheet,
            cash_flow=data.cash_flow_statement,
            prev_income_stmt=data.previous_income_statement,
            prev_balance_sheet=data.previous_balance_sheet,
        )

        profitability = ratios.profitability()
        safety = ratios.safety()
        efficiency = ratios.efficiency()
        growth = ratios.growth()
        cf = ratios.cash_flow_ratios()

        result = AnalysisResult(
            company_name=data.company_name,
            period=data.income_statement.period,
            profitability=profitability,
            safety=safety,
            efficiency=efficiency,
            growth=growth,
            cash_flow=cf,
        )

        result.profitability_comments = self._evaluate_profitability(profitability)
        result.safety_comments = self._evaluate_safety(safety)
        result.efficiency_comments = self._evaluate_efficiency(efficiency)
        result.growth_comments = self._evaluate_growth(growth)
        result.cash_flow_comments = self._evaluate_cash_flow(cf)
        result.overall_score, result.overall_comments = self._overall_evaluation(result)

        return result

    def _evaluate_profitability(self, r: ProfitabilityRatios) -> List[str]:
        comments = []

        if r.gross_profit_margin >= 50:
            comments.append(f"売上総利益率 {r.gross_profit_margin:.1f}% — 非常に高い粗利率。強固な価格競争力があります。")
        elif r.gross_profit_margin >= 30:
            comments.append(f"売上総利益率 {r.gross_profit_margin:.1f}% — 良好な粗利率を維持しています。")
        elif r.gross_profit_margin >= 10:
            comments.append(f"売上総利益率 {r.gross_profit_margin:.1f}% — 業種によっては標準的な水準です。")
        else:
            comments.append(f"売上総利益率 {r.gross_profit_margin:.1f}% — 粗利率が低く、原価管理の改善が必要です。")

        if r.operating_profit_margin >= 15:
            comments.append(f"営業利益率 {r.operating_profit_margin:.1f}% — 優れた収益力を示しています。")
        elif r.operating_profit_margin >= 5:
            comments.append(f"営業利益率 {r.operating_profit_margin:.1f}% — 安定した営業収益を確保しています。")
        elif r.operating_profit_margin >= 0:
            comments.append(f"営業利益率 {r.operating_profit_margin:.1f}% — 収益性の改善が課題です。")
        else:
            comments.append(f"営業利益率 {r.operating_profit_margin:.1f}% — 営業損失が発生しており、早急な対策が必要です。")

        if r.return_on_equity >= 15:
            comments.append(f"ROE {r.return_on_equity:.1f}% — 株主資本を効率的に活用し、高い収益を生み出しています。")
        elif r.return_on_equity >= 8:
            comments.append(f"ROE {r.return_on_equity:.1f}% — 資本効率は標準的な水準です。")
        else:
            comments.append(f"ROE {r.return_on_equity:.1f}% — 資本効率の改善が望まれます。")

        return comments

    def _evaluate_safety(self, r: SafetyRatios) -> List[str]:
        comments = []

        if r.current_ratio >= 200:
            comments.append(f"流動比率 {r.current_ratio:.1f}% — 短期的な支払い能力は十分です。")
        elif r.current_ratio >= 100:
            comments.append(f"流動比率 {r.current_ratio:.1f}% — 流動性は概ね問題ありません。")
        else:
            comments.append(f"流動比率 {r.current_ratio:.1f}% — 流動性リスクがあります。短期借入金の管理に注意が必要です。")

        if r.equity_ratio >= 50:
            comments.append(f"自己資本比率 {r.equity_ratio:.1f}% — 財務基盤が非常に健全です。")
        elif r.equity_ratio >= 30:
            comments.append(f"自己資本比率 {r.equity_ratio:.1f}% — 健全な財務構造を維持しています。")
        elif r.equity_ratio >= 15:
            comments.append(f"自己資本比率 {r.equity_ratio:.1f}% — 財務レバレッジが高めです。")
        else:
            comments.append(f"自己資本比率 {r.equity_ratio:.1f}% — 財務基盤の強化が急務です。")

        if r.interest_coverage_ratio is not None:
            if r.interest_coverage_ratio >= 5:
                comments.append(f"インタレスト・カバレッジ・レシオ {r.interest_coverage_ratio:.1f}倍 — 利息支払い能力は十分です。")
            elif r.interest_coverage_ratio >= 2:
                comments.append(f"インタレスト・カバレッジ・レシオ {r.interest_coverage_ratio:.1f}倍 — 利息支払いは可能ですが余裕は少ないです。")
            else:
                comments.append(f"インタレスト・カバレッジ・レシオ {r.interest_coverage_ratio:.1f}倍 — 利息支払い能力に懸念があります。")

        return comments

    def _evaluate_efficiency(self, r: EfficiencyRatios) -> List[str]:
        comments = []

        if r.asset_turnover >= 1.5:
            comments.append(f"総資産回転率 {r.asset_turnover:.2f}回 — 資産を効率的に活用して売上を生み出しています。")
        elif r.asset_turnover >= 0.8:
            comments.append(f"総資産回転率 {r.asset_turnover:.2f}回 — 資産効率は標準的な水準です。")
        else:
            comments.append(f"総資産回転率 {r.asset_turnover:.2f}回 — 資産活用効率の改善余地があります。")

        if r.days_sales_outstanding is not None:
            if r.days_sales_outstanding <= 30:
                comments.append(f"売掛金回収日数 {r.days_sales_outstanding:.0f}日 — 迅速な代金回収ができています。")
            elif r.days_sales_outstanding <= 60:
                comments.append(f"売掛金回収日数 {r.days_sales_outstanding:.0f}日 — 売掛金回収は標準的な水準です。")
            else:
                comments.append(f"売掛金回収日数 {r.days_sales_outstanding:.0f}日 — 回収サイクルが長く、改善が望まれます。")

        return comments

    def _evaluate_growth(self, r: GrowthRatios) -> List[str]:
        comments = []

        if r.revenue_growth_rate is None:
            comments.append("成長率の算出には前期データが必要です。")
            return comments

        if r.revenue_growth_rate >= 20:
            comments.append(f"売上高成長率 {r.revenue_growth_rate:.1f}% — 高い成長を実現しています。")
        elif r.revenue_growth_rate >= 5:
            comments.append(f"売上高成長率 {r.revenue_growth_rate:.1f}% — 安定した増収を達成しています。")
        elif r.revenue_growth_rate >= 0:
            comments.append(f"売上高成長率 {r.revenue_growth_rate:.1f}% — 売上はほぼ横ばいです。")
        else:
            comments.append(f"売上高成長率 {r.revenue_growth_rate:.1f}% — 売上が減少しています。原因の分析が必要です。")

        if r.operating_income_growth_rate is not None:
            if r.operating_income_growth_rate >= 10:
                comments.append(f"営業利益成長率 {r.operating_income_growth_rate:.1f}% — 利益の改善が顕著です。")
            elif r.operating_income_growth_rate < 0:
                comments.append(f"営業利益成長率 {r.operating_income_growth_rate:.1f}% — 利益が減少しています。費用管理の見直しが必要です。")

        return comments

    def _evaluate_cash_flow(self, r: CashFlowRatios) -> List[str]:
        comments = []

        if r.operating_cf_margin >= 15:
            comments.append(f"営業CFマージン {r.operating_cf_margin:.1f}% — キャッシュ創出力が優れています。")
        elif r.operating_cf_margin >= 5:
            comments.append(f"営業CFマージン {r.operating_cf_margin:.1f}% — 安定したキャッシュフローを確保しています。")
        else:
            comments.append(f"営業CFマージン {r.operating_cf_margin:.1f}% — キャッシュ創出力の改善が必要です。")

        if r.free_cash_flow >= 0:
            comments.append(f"フリーキャッシュフロー {r.free_cash_flow:,.0f}円 — プラスで事業の自己資金調達能力があります。")
        else:
            comments.append(f"フリーキャッシュフロー {r.free_cash_flow:,.0f}円 — マイナスです。投資フェーズにあるか、キャッシュ管理の改善が必要です。")

        return comments

    def _overall_evaluation(self, result: AnalysisResult):
        """総合評価スコア（0〜100）とコメントを算出する"""
        score = 0.0
        max_score = 0.0
        comments = []

        # 収益性 (30点満点)
        p = result.profitability
        max_score += 30
        if p.operating_profit_margin >= 15:
            score += 30
        elif p.operating_profit_margin >= 5:
            score += 20
        elif p.operating_profit_margin >= 0:
            score += 10

        # 安全性 (30点満点)
        s = result.safety
        max_score += 30
        safety_pts = 0
        if s.equity_ratio >= 50:
            safety_pts += 15
        elif s.equity_ratio >= 30:
            safety_pts += 10
        elif s.equity_ratio >= 15:
            safety_pts += 5

        if s.current_ratio >= 200:
            safety_pts += 15
        elif s.current_ratio >= 100:
            safety_pts += 10
        elif s.current_ratio >= 50:
            safety_pts += 5
        score += safety_pts

        # 効率性 (20点満点)
        e = result.efficiency
        max_score += 20
        if e.asset_turnover >= 1.5:
            score += 20
        elif e.asset_turnover >= 0.8:
            score += 13
        else:
            score += 5

        # CF (20点満点)
        cf = result.cash_flow
        max_score += 20
        if cf.free_cash_flow >= 0 and cf.operating_cf_margin >= 10:
            score += 20
        elif cf.free_cash_flow >= 0:
            score += 13
        elif cf.operating_cf_margin >= 5:
            score += 8

        normalized_score = (score / max_score) * 100 if max_score > 0 else 0

        if normalized_score >= 80:
            comments.append("財務状況は非常に良好です。高い収益性・安全性・資本効率を兼ね備えています。")
        elif normalized_score >= 60:
            comments.append("財務状況は概ね健全です。一部の指標に改善余地がありますが、安定した経営基盤を持っています。")
        elif normalized_score >= 40:
            comments.append("財務状況に改善が必要な点があります。収益性または安全性の強化を検討してください。")
        else:
            comments.append("財務状況に重大な課題があります。早急な経営改善策の実施が求められます。")

        return round(normalized_score, 1), comments
