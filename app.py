"""
栄養管理アプリ - Web UI

毎食の写真（またはテキスト検索）から栄養素を記録し、目標達成度を管理するWebアプリです。

起動方法:
  pip install -r requirements.txt
  streamlit run app.py

ブラウザで http://localhost:8501 が自動的に開きます。

AI写真解析（Claude Vision）を使うには環境変数 ANTHROPIC_API_KEY を設定してください。
未設定の場合は手動検索での記録のみ利用できます。
"""

import os
import sys
from datetime import date, timedelta

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nutrition_tracker import (
    MEAL_TYPES,
    DailyGoal,
    FoodEntry,
    FoodDatabase,
    NutritionInfo,
    NutritionStorage,
    VisionAnalyzerError,
    analyze_photo,
    daily_totals_in_range,
    summarize_by_meal,
    summarize_day,
    vision_is_available,
)

st.set_page_config(page_title="栄養管理アプリ", page_icon="🍱", layout="wide")


@st.cache_resource
def get_storage() -> NutritionStorage:
    return NutritionStorage()


@st.cache_resource
def get_food_db() -> FoodDatabase:
    return FoodDatabase()


storage = get_storage()
food_db = get_food_db()

st.title("🍱 栄養管理アプリ")
st.caption("毎食の写真や手動入力から、カロリー・栄養素を記録して管理します")

# ─────────────────────────────────────────
# サイドバー：対象日・目標値設定
# ─────────────────────────────────────────
with st.sidebar:
    st.header("設定")
    selected_date = st.date_input("対象日", value=date.today())

    st.subheader("1日の目標値")
    saved_goal = storage.get_goal()
    g_calories = st.number_input("カロリー (kcal)", min_value=0.0, value=saved_goal.calories, step=50.0)
    g_protein = st.number_input("たんぱく質 (g)", min_value=0.0, value=saved_goal.protein, step=5.0)
    g_fat = st.number_input("脂質 (g)", min_value=0.0, value=saved_goal.fat, step=5.0)
    g_carbs = st.number_input("炭水化物 (g)", min_value=0.0, value=saved_goal.carbohydrates, step=10.0)
    g_salt = st.number_input("塩分 (g)", min_value=0.0, value=saved_goal.salt, step=0.5)
    if st.button("目標を保存", width="stretch"):
        storage.save_goal(
            DailyGoal(
                calories=g_calories,
                protein=g_protein,
                fat=g_fat,
                carbohydrates=g_carbs,
                salt=g_salt,
            )
        )
        st.success("目標を保存しました")
        st.rerun()

    st.divider()
    if vision_is_available():
        st.success("🤖 AI写真解析: 利用可能")
    else:
        st.warning(
            "🤖 AI写真解析: 利用不可\n\n"
            "環境変数 `ANTHROPIC_API_KEY` が未設定です。「手動で検索」をご利用ください。"
        )

current_goal = storage.get_goal()

tab_add, tab_summary, tab_history = st.tabs(["📝 記録する", "📊 今日のまとめ", "📈 履歴"])

# ─────────────────────────────────────────
# 記録する
# ─────────────────────────────────────────
with tab_add:
    meal_type = st.radio("食事の種類", options=MEAL_TYPES, horizontal=True)
    method = st.radio(
        "記録方法", options=["📷 写真から解析 (AI)", "🔍 手動で検索"], horizontal=True
    )

    if method == "📷 写真から解析 (AI)":
        if not vision_is_available():
            st.warning(
                "AI写真解析を使うには `ANTHROPIC_API_KEY` を設定してください。"
                "「手動で検索」をご利用ください。"
            )
        else:
            uploaded = st.file_uploader(
                "食事の写真をアップロード",
                type=["jpg", "jpeg", "png", "webp"],
                key="photo_uploader",
            )
            camera_photo = st.camera_input("またはカメラで撮影")
            photo_file = uploaded or camera_photo

            if photo_file is not None:
                st.image(photo_file, caption="アップロードされた写真", width=300)
                if st.button("🤖 AIで解析する"):
                    with st.spinner("写真を解析中..."):
                        try:
                            result = analyze_photo(
                                photo_file.getvalue(),
                                filename=getattr(photo_file, "name", "photo.jpg") or "photo.jpg",
                            )
                            st.session_state["analysis_result"] = result
                        except VisionAnalyzerError as e:
                            st.error(f"解析エラー: {e}")
                            st.session_state.pop("analysis_result", None)

            result = st.session_state.get("analysis_result")
            if result is not None:
                st.subheader("解析結果（必要に応じて編集してください）")
                edited_items = []
                for i, item in enumerate(result.items):
                    with st.expander(f"🍽️ {item.name}", expanded=True):
                        c1, c2 = st.columns(2)
                        name = c1.text_input("食品名", value=item.name, key=f"name_{i}")
                        qty = c2.number_input(
                            "量 (g)", min_value=0.0, value=item.quantity_g, step=10.0, key=f"qty_{i}"
                        )
                        c3, c4, c5, c6 = st.columns(4)
                        cal = c3.number_input(
                            "カロリー(kcal)", min_value=0.0, value=item.calories, key=f"cal_{i}"
                        )
                        pro = c4.number_input(
                            "たんぱく質(g)", min_value=0.0, value=item.protein, key=f"pro_{i}"
                        )
                        fat = c5.number_input("脂質(g)", min_value=0.0, value=item.fat, key=f"fat_{i}")
                        carb = c6.number_input(
                            "炭水化物(g)", min_value=0.0, value=item.carbohydrates, key=f"carb_{i}"
                        )
                        c7, c8 = st.columns(2)
                        sugar = c7.number_input(
                            "糖質(g)", min_value=0.0, value=item.sugar, key=f"sugar_{i}"
                        )
                        fiber = c8.number_input(
                            "食物繊維(g)", min_value=0.0, value=item.fiber, key=f"fiber_{i}"
                        )
                        salt = st.number_input(
                            "塩分(g)", min_value=0.0, value=item.salt, key=f"salt_{i}"
                        )
                        edited_items.append(
                            (name, qty, NutritionInfo(cal, pro, fat, carb, sugar, fiber, salt))
                        )

                if st.button("✅ この内容を記録する", type="primary"):
                    for name, qty, nutrition in edited_items:
                        storage.add_entry(
                            FoodEntry(
                                food_name=name,
                                nutrition=nutrition,
                                meal_type=meal_type,
                                quantity_g=qty,
                                entry_date=selected_date,
                                source="ai",
                            )
                        )
                    st.success(f"{len(edited_items)}件の食事を記録しました")
                    st.session_state.pop("analysis_result", None)
                    st.rerun()

    else:
        query = st.text_input("食品名で検索", placeholder="例: 白米, 鶏むね肉, バナナ")
        matches = food_db.search(query) if query else food_db.all_records[:20]
        if matches:
            options = {f"{r.name} ({r.category})": r for r in matches}
            selected_label = st.selectbox("食品を選択", options=list(options.keys()))
            selected_record = options[selected_label]
            quantity = st.number_input("量 (g)", min_value=0.0, value=100.0, step=10.0)
            nutrition = selected_record.nutrition_per_100g.scaled(quantity / 100.0)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("カロリー", f"{nutrition.calories:.0f} kcal")
            c2.metric("たんぱく質", f"{nutrition.protein:.1f} g")
            c3.metric("脂質", f"{nutrition.fat:.1f} g")
            c4.metric("炭水化物", f"{nutrition.carbohydrates:.1f} g")
            c5.metric("塩分", f"{nutrition.salt:.1f} g")

            if st.button("✅ この内容を記録する", type="primary", key="manual_add"):
                storage.add_entry(
                    FoodEntry(
                        food_name=selected_record.name,
                        nutrition=nutrition,
                        meal_type=meal_type,
                        quantity_g=quantity,
                        entry_date=selected_date,
                        source="manual",
                    )
                )
                st.success(f"{selected_record.name} を記録しました")
                st.rerun()
        else:
            st.info("該当する食品が見つかりませんでした。")

# ─────────────────────────────────────────
# 今日のまとめ
# ─────────────────────────────────────────
with tab_summary:
    entries = storage.get_entries_by_date(selected_date)
    summary = summarize_day(selected_date, entries, current_goal)

    st.subheader(f"📅 {selected_date.isoformat()} のまとめ")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        "カロリー",
        f"{summary.total.calories:.0f} / {current_goal.calories:.0f} kcal",
        f"{summary.calories_ratio:.0f}%",
    )
    c2.metric(
        "たんぱく質",
        f"{summary.total.protein:.1f} / {current_goal.protein:.1f} g",
        f"{summary.protein_ratio:.0f}%",
    )
    c3.metric(
        "脂質", f"{summary.total.fat:.1f} / {current_goal.fat:.1f} g", f"{summary.fat_ratio:.0f}%"
    )
    c4.metric(
        "炭水化物",
        f"{summary.total.carbohydrates:.1f} / {current_goal.carbohydrates:.1f} g",
        f"{summary.carbohydrates_ratio:.0f}%",
    )
    c5.metric(
        "塩分", f"{summary.total.salt:.1f} / {current_goal.salt:.1f} g", f"{summary.salt_ratio:.0f}%"
    )

    st.progress(
        min(summary.calories_ratio / 100, 1.0),
        text=f"カロリー目標達成率 {summary.calories_ratio:.0f}%",
    )

    if entries:
        macro_df = pd.DataFrame(
            {
                "栄養素": ["たんぱく質", "脂質", "炭水化物"],
                "グラム": [summary.total.protein, summary.total.fat, summary.total.carbohydrates],
            }
        ).set_index("栄養素")
        st.bar_chart(macro_df)

        st.subheader("食事内容")
        meal_totals = summarize_by_meal(entries)
        for meal in MEAL_TYPES:
            meal_entries = [e for e in entries if e.meal_type == meal]
            if not meal_entries:
                continue
            total = meal_totals.get(meal, NutritionInfo())
            st.markdown(f"**{meal}** — {total.calories:.0f} kcal")
            for e in meal_entries:
                cols = st.columns([4, 2, 2, 1])
                cols[0].write(f"{e.food_name} ({e.quantity_g:.0f}g)")
                cols[1].write(f"{e.nutrition.calories:.0f} kcal")
                cols[2].write("🤖 AI" if e.source == "ai" else "✍️ 手動")
                if cols[3].button("削除", key=f"del_{e.entry_id}"):
                    storage.delete_entry(e.entry_id)
                    st.rerun()
    else:
        st.info("この日の記録はまだありません。「記録する」タブから追加してください。")

# ─────────────────────────────────────────
# 履歴
# ─────────────────────────────────────────
with tab_history:
    st.subheader("📈 期間トレンド")
    c1, c2 = st.columns(2)
    start_date = c1.date_input("開始日", value=date.today() - timedelta(days=6), key="hist_start")
    end_date = c2.date_input("終了日", value=date.today(), key="hist_end")

    if start_date > end_date:
        st.error("開始日は終了日より前にしてください。")
    else:
        range_entries = storage.get_entries_in_range(start_date, end_date)
        totals_by_date = daily_totals_in_range(range_entries)

        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        trend_df = pd.DataFrame(
            {
                "日付": [d.isoformat() for d in all_dates],
                "カロリー": [totals_by_date.get(d, NutritionInfo()).calories for d in all_dates],
            }
        ).set_index("日付")
        st.line_chart(trend_df)

        st.subheader("記録一覧")
        if range_entries:
            table_df = pd.DataFrame(
                [
                    {
                        "日付": e.entry_date.isoformat(),
                        "食事": e.meal_type,
                        "食品名": e.food_name,
                        "量(g)": e.quantity_g,
                        "カロリー": e.nutrition.calories,
                        "たんぱく質": e.nutrition.protein,
                        "脂質": e.nutrition.fat,
                        "炭水化物": e.nutrition.carbohydrates,
                        "記録方法": "AI" if e.source == "ai" else "手動",
                    }
                    for e in range_entries
                ]
            )
            st.dataframe(table_df, width="stretch", hide_index=True)
        else:
            st.info("この期間の記録はありません。")
