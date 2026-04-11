"""
財務分析ツール - Web UI

ブラウザからファイルをアップロードして財務分析を実行するWebアプリです。

起動方法:
  pip install streamlit
  streamlit run app.py

ブラウザで http://localhost:8501 が自動的に開きます。
"""

import io
import sys
import os
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from financial_analysis import (
    FinancialAnalyzer,
    ReportGenerator,
    load_financial_data,
)

# ページ設定
st.set_page_config(
    page_title="財務分析ツール",
    page_icon="📊",
    layout="wide",
)

# ヘッダー
st.title("📊 財務分析ツール")
st.caption("損益計算書（PDF / Excel / Word）をアップロードして財務指標を自動分析します")

# ─────────────────────────────────────────
# サイドバー：入力オプション
# ─────────────────────────────────────────
with st.sidebar:
    st.header("設定")

    company_name = st.text_input(
        "企業名",
        placeholder="例: 株式会社〇〇",
        help="省略するとファイル名が使われます",
    )
    period = st.text_input(
        "会計期間",
        placeholder="例: 2024年3月期",
    )
    unit = st.selectbox(
        "金額単位",
        options=[1, 1_000, 1_000_000],
        format_func=lambda x: {1: "円", 1_000: "千円", 1_000_000: "百万円"}[x],
        index=0,
    )
    sheet_name = st.text_input(
        "Excelシート名（任意）",
        placeholder="例: 損益計算書",
        help="省略すると「損益」を含むシートを自動選択します",
    )
    report_format = st.radio(
        "レポート形式",
        options=["テキスト", "Markdown"],
        horizontal=True,
    )

# ─────────────────────────────────────────
# メインエリア：ファイルアップロード
# ─────────────────────────────────────────
uploaded_file = st.file_uploader(
    "ファイルをドラッグ＆ドロップ、またはクリックして選択",
    type=["pdf", "xlsx", "xls", "xlsm", "docx"],
    help="対応形式: PDF / Excel (.xlsx .xls) / Word (.docx)",
)

if uploaded_file is not None:
    st.success(f"ファイルを受け取りました: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

    with st.spinner("分析中..."):
        # 一時ファイルに保存
        suffix = Path(uploaded_file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            data = load_financial_data(
                tmp_path,
                company_name=company_name or "",
                period=period or "",
                unit=float(unit),
                sheet_name=sheet_name or None,
            )
        except Exception as e:
            st.error(f"読み込みエラー: {e}")
            os.unlink(tmp_path)
            st.stop()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # ─────────────────────────────────────────
    # 抽出結果サマリー
    # ─────────────────────────────────────────
    is_ = data.income_statement
    st.subheader(f"📋 抽出結果: {data.company_name}  {is_.period}")

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("売上高", is_.revenue),
        ("売上原価", is_.cost_of_goods_sold),
        ("売上総利益", is_.gross_profit),
        ("営業利益", is_.operating_income),
        ("当期純利益", is_.net_income),
    ]
    for col, (label, val) in zip([col1, col2, col3, col4, col5], metrics):
        unit_label = {1: "円", 1_000: "千円", 1_000_000: "百万円"}[unit]
        col.metric(label, f"{val:,.0f} {unit_label}")

    if not is_.revenue:
        st.warning(
            "売上高が0です。ファイルの科目名が標準的な表記（売上高・売上原価 等）と"
            "異なる可能性があります。"
        )

    st.divider()

    # ─────────────────────────────────────────
    # 財務分析レポート
    # ─────────────────────────────────────────
    analyzer = FinancialAnalyzer()
    generator = ReportGenerator()
    result = analyzer.analyze(data)

    st.subheader("📈 財務分析レポート")

    # 総合スコア
    score = result.overall_score
    score_color = "green" if score >= 70 else ("orange" if score >= 50 else "red")
    st.metric("総合評価スコア", f"{score:.1f} / 100")
    st.progress(score / 100)
    for c in result.overall_comments:
        st.info(c)

    # 4カテゴリをタブで表示
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["収益性", "安全性", "効率性", "成長性", "キャッシュフロー"]
    )

    with tab1:
        p = result.profitability
        c1, c2, c3 = st.columns(3)
        c1.metric("売上総利益率", f"{p.gross_profit_margin:.1f}%")
        c2.metric("営業利益率", f"{p.operating_profit_margin:.1f}%")
        c3.metric("純利益率", f"{p.net_profit_margin:.1f}%")
        c1b, c2b, c3b = st.columns(3)
        c1b.metric("ROA", f"{p.return_on_assets:.1f}%")
        c2b.metric("ROE", f"{p.return_on_equity:.1f}%")
        if p.ebitda_margin is not None:
            c3b.metric("EBITDAマージン", f"{p.ebitda_margin:.1f}%")
        for c in result.profitability_comments:
            st.write(f"・{c}")

    with tab2:
        s = result.safety
        c1, c2, c3 = st.columns(3)
        c1.metric("流動比率", f"{s.current_ratio:.1f}%")
        c2.metric("自己資本比率", f"{s.equity_ratio:.1f}%")
        c3.metric("負債資本比率", f"{s.debt_to_equity_ratio:.2f}倍")
        if s.interest_coverage_ratio is not None:
            st.metric("インタレスト・カバレッジ・レシオ", f"{s.interest_coverage_ratio:.1f}倍")
        for c in result.safety_comments:
            st.write(f"・{c}")

    with tab3:
        e = result.efficiency
        c1, c2 = st.columns(2)
        c1.metric("総資産回転率", f"{e.asset_turnover:.2f}回")
        if e.days_sales_outstanding is not None:
            c2.metric("売掛金回収日数", f"{e.days_sales_outstanding:.0f}日")
        if e.inventory_turnover is not None:
            c1b, c2b = st.columns(2)
            c1b.metric("棚卸資産回転率", f"{e.inventory_turnover:.2f}回")
            if e.days_inventory_outstanding is not None:
                c2b.metric("棚卸資産回転日数", f"{e.days_inventory_outstanding:.0f}日")
        for c in result.efficiency_comments:
            st.write(f"・{c}")

    with tab4:
        g = result.growth
        if g.revenue_growth_rate is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("売上高成長率", f"{g.revenue_growth_rate:+.1f}%")
            if g.operating_income_growth_rate is not None:
                c2.metric("営業利益成長率", f"{g.operating_income_growth_rate:+.1f}%")
            if g.net_income_growth_rate is not None:
                c3.metric("純利益成長率", f"{g.net_income_growth_rate:+.1f}%")
        for c in result.growth_comments:
            st.write(f"・{c}")

    with tab5:
        cf = result.cash_flow
        c1, c2 = st.columns(2)
        c1.metric("営業CFマージン", f"{cf.operating_cf_margin:.1f}%")
        c2.metric("フリーキャッシュフロー", f"{cf.free_cash_flow:,.0f}円")
        for c in result.cash_flow_comments:
            st.write(f"・{c}")

    st.divider()

    # ─────────────────────────────────────────
    # レポートダウンロード
    # ─────────────────────────────────────────
    st.subheader("⬇️ レポートをダウンロード")

    if report_format == "Markdown":
        report_text = generator.generate_markdown(result)
        filename = f"財務分析_{data.company_name}.md"
        mime = "text/markdown"
    else:
        report_text = generator.generate_text(result)
        filename = f"財務分析_{data.company_name}.txt"
        mime = "text/plain"

    st.download_button(
        label=f"📥 {filename} をダウンロード",
        data=report_text.encode("utf-8"),
        file_name=filename,
        mime=mime,
    )

else:
    # アップロード前の案内
    st.info(
        "👆 上のエリアにファイルをドラッグ＆ドロップするか、クリックしてファイルを選択してください。\n\n"
        "**対応形式:** PDF / Excel (.xlsx .xls) / Word (.docx)"
    )

    with st.expander("対応している表の形式について"):
        st.markdown("""
**パターンA：科目が行・月が列（最も一般的）**
```
勘定科目  | 4月  | 5月  | ... | 合計
売上高    | 100  | 110  | ... | 1200
売上原価  | 40   | 44   | ... | 480
...
```

**パターンB：月が行・科目が列**
```
月   | 売上高 | 売上原価 | ...
4月  | 100   | 40      | ...
5月  | 110   | 44      | ...
```
        """)
