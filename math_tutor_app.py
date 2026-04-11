"""
中学2年生 仮想数学塾
予習・復習・AI講師チャットを組み合わせた対話型学習アプリ

起動方法:
  pip install streamlit anthropic
  streamlit run math_tutor_app.py
"""

import random
import os
import sys
import anthropic
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from math_content import UNITS, get_unit, get_problems_for_unit

# ──────────────────────────────────────────────
# ページ設定
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="中2数学 仮想塾",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# セッション状態の初期化
# ──────────────────────────────────────────────
def _init_session():
    defaults = {
        "page": "home",
        "selected_unit": None,
        "progress": {u["id"]: {"studied": False, "correct": 0, "total": 0} for u in UNITS},
        "chat_history": [],
        "quiz_state": None,   # {"problems": [...], "idx": 0, "score": 0, "answers": []}
        "show_solution": False,
        "answered": False,
        "selected_choice": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ──────────────────────────────────────────────
# ユーティリティ
# ──────────────────────────────────────────────
def go(page: str, unit_id: str | None = None):
    st.session_state.page = page
    if unit_id is not None:
        st.session_state.selected_unit = unit_id
    # クイズ状態のリセット
    if page == "quiz":
        st.session_state.quiz_state = None
        st.session_state.show_solution = False
        st.session_state.answered = False
        st.session_state.selected_choice = None
    st.rerun()


def progress_bar_color(pct: float) -> str:
    if pct >= 80:
        return "green"
    elif pct >= 50:
        return "orange"
    return "red"


def total_stats():
    total_correct = sum(p["correct"] for p in st.session_state.progress.values())
    total_q = sum(p["total"] for p in st.session_state.progress.values())
    studied = sum(1 for p in st.session_state.progress.values() if p["studied"])
    return studied, total_correct, total_q


# ──────────────────────────────────────────────
# サイドバー
# ──────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.title("📚 中2数学 仮想塾")
        st.caption("予習・復習・AI講師で効率よく学ぼう！")
        st.divider()

        if st.button("🏠 ホーム", use_container_width=True,
                     type="primary" if st.session_state.page == "home" else "secondary"):
            go("home")

        st.markdown("**単元を選ぶ**")
        for unit in UNITS:
            prog = st.session_state.progress[unit["id"]]
            studied_mark = "✅ " if prog["studied"] else ""
            label = f"{unit['icon']} {studied_mark}{unit['title']}"
            is_active = st.session_state.selected_unit == unit["id"]
            if st.button(label, key=f"nav_{unit['id']}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                go("unit", unit["id"])

        st.divider()
        if st.button("🤖 AI講師に質問", use_container_width=True,
                     type="primary" if st.session_state.page == "chat" else "secondary"):
            go("chat")

        st.divider()
        studied, correct, total_q = total_stats()
        st.markdown(f"**学習進捗**")
        st.markdown(f"- 学習済み単元: **{studied} / {len(UNITS)}**")
        if total_q > 0:
            acc = correct / total_q * 100
            st.markdown(f"- 問題正答率: **{acc:.0f}%** ({correct}/{total_q})")
        else:
            st.markdown("- まだ問題を解いていません")


# ──────────────────────────────────────────────
# ホーム画面
# ──────────────────────────────────────────────
def render_home():
    st.title("📚 中学2年生 仮想数学塾へようこそ！")
    st.markdown("""
ここでは中学2年生の数学を効率よく **予習・復習** できます。

| 機能 | 説明 |
|------|------|
| 📖 単元学習 | 左メニューから単元を選んで説明を読む（予習・復習） |
| ✏️ 練習問題 | 各単元の問題を解いて実力チェック |
| 🤖 AI講師 | わからないことをAIに質問する |
""")

    st.divider()
    st.subheader("📊 あなたの学習ダッシュボード")

    cols = st.columns(len(UNITS))
    for col, unit in zip(cols, UNITS):
        prog = st.session_state.progress[unit["id"]]
        with col:
            studied_txt = "学習済み ✅" if prog["studied"] else "未学習"
            total = prog["total"]
            correct = prog["correct"]
            acc_txt = f"{correct}/{total}" if total > 0 else "未挑戦"
            st.metric(
                label=f"{unit['icon']} {unit['title']}",
                value=acc_txt,
                delta=studied_txt,
            )

    st.divider()
    st.subheader("今日はどこから始める？")
    btn_cols = st.columns(len(UNITS))
    for col, unit in zip(btn_cols, UNITS):
        with col:
            if st.button(f"{unit['icon']} {unit['title']}", key=f"home_{unit['id']}",
                         use_container_width=True):
                go("unit", unit["id"])


# ──────────────────────────────────────────────
# 単元学習画面
# ──────────────────────────────────────────────
def render_unit():
    unit_id = st.session_state.selected_unit
    unit = get_unit(unit_id)
    if unit is None:
        st.error("単元が見つかりません。")
        return

    # 学習済みフラグを立てる
    st.session_state.progress[unit_id]["studied"] = True

    st.title(f"{unit['icon']} {unit['title']}")
    st.caption(unit["description"])

    tab_labels = ["📖 学習内容"] + [s["name"] for s in unit["sections"]] + ["📐 重要公式", "✏️ 練習問題へ"]
    tabs = st.tabs(tab_labels)

    # ── 概要タブ ──
    with tabs[0]:
        st.markdown(f"### {unit['title']} の学習内容")
        for i, sec in enumerate(unit["sections"], 1):
            st.markdown(f"**{i}. {sec['name']}**")
        st.info("上のタブを切り替えて各項目を学習しましょう！")

    # ── セクションタブ ──
    for i, (sec, tab) in enumerate(zip(unit["sections"], tabs[1: 1 + len(unit["sections"])])):
        with tab:
            st.markdown(f"## {sec['name']}")
            st.markdown(sec["explanation"])

    # ── 重要公式タブ ──
    with tabs[-2]:
        st.markdown("### 重要公式一覧")
        for kf in unit["key_formulas"]:
            st.markdown(f"**{kf['label']}**")
            st.latex(kf["formula"])
            st.divider()

    # ── 練習問題へボタン ──
    with tabs[-1]:
        st.markdown("### 練習問題に挑戦しよう！")
        problems = get_problems_for_unit(unit_id)
        st.markdown(f"この単元には **{len(problems)}問** の練習問題があります。")
        if st.button("✏️ 練習問題をはじめる", type="primary", use_container_width=True):
            go("quiz", unit_id)


# ──────────────────────────────────────────────
# 練習問題画面
# ──────────────────────────────────────────────
def render_quiz():
    unit_id = st.session_state.selected_unit
    unit = get_unit(unit_id)
    problems = get_problems_for_unit(unit_id)

    if not problems:
        st.warning("この単元の問題はまだ準備中です。")
        return

    # クイズ初期化
    if st.session_state.quiz_state is None:
        shuffled = problems.copy()
        random.shuffle(shuffled)
        st.session_state.quiz_state = {
            "problems": shuffled,
            "idx": 0,
            "score": 0,
            "answers": [],
            "finished": False,
        }

    qs = st.session_state.quiz_state

    # ─ 結果画面 ─
    if qs["finished"]:
        _render_quiz_result(unit, qs)
        return

    current = qs["problems"][qs["idx"]]
    total = len(qs["problems"])
    idx = qs["idx"]

    # ヘッダー
    col_title, col_progress = st.columns([3, 1])
    with col_title:
        st.title(f"{unit['icon']} {unit['title']} 練習問題")
    with col_progress:
        st.metric("進捗", f"{idx + 1} / {total}")
        st.progress((idx + 1) / total)

    st.divider()

    # 問題文
    level_star = "⭐" * current["level"]
    st.markdown(f"**問題 {idx + 1}** &nbsp;&nbsp; 難易度: {level_star}")
    st.markdown(f"### {current['question']}")

    # 選択肢
    choices = current["choices"]
    selected = st.radio(
        "答えを選んでください",
        choices,
        key=f"choice_{idx}",
        index=None,
        horizontal=True,
    )

    col_ans, col_skip = st.columns([1, 1])

    with col_ans:
        if st.button("✅ 答え合わせ", type="primary", disabled=(selected is None),
                     use_container_width=True):
            st.session_state.answered = True
            st.session_state.selected_choice = selected
            st.session_state.show_solution = False
            st.rerun()

    with col_skip:
        if st.button("⏭️ スキップ", use_container_width=True):
            _advance_quiz(qs, current, answered=False, correct=False)
            st.rerun()

    # 答え合わせ後の表示
    if st.session_state.answered and st.session_state.selected_choice is not None:
        chosen = st.session_state.selected_choice
        correct_ans = current["answer"]
        is_correct = (chosen == correct_ans)

        if is_correct:
            st.success("🎉 正解！素晴らしい！")
        else:
            st.error(f"❌ 不正解。正解は **{correct_ans}** です。")

        # 解説トグル
        if st.button("📝 解説を見る / 隠す"):
            st.session_state.show_solution = not st.session_state.show_solution
            st.rerun()

        if st.session_state.show_solution:
            with st.expander("解説", expanded=True):
                st.markdown(current["solution"])

        # 次の問題へ
        btn_label = "次の問題へ ➡️" if idx + 1 < total else "結果を見る 🏆"
        if st.button(btn_label, type="primary", use_container_width=True):
            _advance_quiz(qs, current, answered=True, correct=is_correct)
            st.session_state.answered = False
            st.session_state.selected_choice = None
            st.session_state.show_solution = False
            st.rerun()

    # AI講師へのリンク
    st.divider()
    st.caption("わからなかったら 🤖 AI講師に質問しよう！")
    if st.button("🤖 AI講師に質問する"):
        # 問題をチャット入力として渡す
        question_text = f"【{unit['title']}】{current['question']} がわかりません。解き方を教えてください。"
        st.session_state.chat_history.append({"role": "user", "content": question_text})
        go("chat")


def _advance_quiz(qs: dict, current: dict, answered: bool, correct: bool):
    if answered:
        qs["answers"].append({"id": current["id"], "correct": correct})
        if correct:
            qs["score"] += 1
    else:
        qs["answers"].append({"id": current["id"], "correct": False, "skipped": True})

    if qs["idx"] + 1 >= len(qs["problems"]):
        qs["finished"] = True
        # 進捗に反映
        unit_id = st.session_state.selected_unit
        prog = st.session_state.progress[unit_id]
        prog["total"] += len(qs["problems"])
        prog["correct"] += qs["score"]
    else:
        qs["idx"] += 1


def _render_quiz_result(unit: dict, qs: dict):
    total = len(qs["problems"])
    score = qs["score"]
    pct = score / total * 100

    st.title(f"{unit['icon']} {unit['title']} 結果発表！")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", f"{score} / {total}")
        st.metric("正答率", f"{pct:.0f}%")
    with col2:
        if pct == 100:
            st.balloons()
            st.success("🏆 パーフェクト！完璧です！")
        elif pct >= 80:
            st.success("👏 よくできました！もう少しで満点！")
        elif pct >= 60:
            st.warning("📖 まあまあです。解説を読み直しましょう。")
        else:
            st.error("😅 もう一度学習内容を確認してから挑戦しよう！")

    st.divider()
    st.subheader("問題ごとの振り返り")
    for i, (problem, ans_rec) in enumerate(zip(qs["problems"], qs["answers"]), 1):
        icon = "✅" if ans_rec.get("correct") else ("⏭️" if ans_rec.get("skipped") else "❌")
        with st.expander(f"{icon} 問題 {i}: {problem['question'][:40]}..."):
            st.markdown(f"**正解**: {problem['answer']}")
            st.markdown("**解説**")
            st.markdown(problem["solution"])

    st.divider()
    col_retry, col_study, col_home = st.columns(3)
    with col_retry:
        if st.button("🔄 もう一度挑戦", use_container_width=True, type="primary"):
            go("quiz", st.session_state.selected_unit)
    with col_study:
        if st.button("📖 学習に戻る", use_container_width=True):
            go("unit", st.session_state.selected_unit)
    with col_home:
        if st.button("🏠 ホームへ", use_container_width=True):
            go("home")


# ──────────────────────────────────────────────
# AIチャット画面
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """あなたは中学2年生向けの優しい数学の先生です。
生徒が数学の問題や概念について質問してきます。
以下のルールを守って回答してください：

1. 中学2年生が理解できる言葉と例を使う
2. 数式は LaTeX 形式（$...$ か $$...$$）で書く
3. 解き方をステップバイステップで説明する
4. 難しい部分は具体的な数値例を使って説明する
5. 励ましの言葉を添えて、自信を持てるようにする
6. 答えをすぐに教えるより、ヒントを使って自分で考えさせる工夫をする
7. 間違いを指摘するときは優しく、どこが間違いか明確に教える

担当する単元：式の計算、連立方程式、一次関数、図形の性質、確率"""


def render_chat():
    st.title("🤖 AI講師チャット")
    st.caption("数学でわからないことを何でも聞いてください！")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.warning(
            "⚠️ ANTHROPIC_API_KEY が設定されていません。\n\n"
            "ターミナルで `export ANTHROPIC_API_KEY=あなたのキー` を実行してから再起動してください。"
        )

    # チャット履歴の表示
    for msg in st.session_state.chat_history:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg["content"])

    # クイックスタートボタン（履歴が空のとき）
    if not st.session_state.chat_history:
        st.markdown("**よくある質問から始める:**")
        quick_qs = [
            "連立方程式の加減法と代入法の違いを教えて",
            "一次関数の傾きってどういう意味？",
            "確率で余事象を使う問題を教えて",
            "三角形の合同条件を全部教えて",
            "式の計算で符号のミスをなくすコツは？",
        ]
        cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            with cols[i % 2]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    st.rerun()

    # チャット入力
    if user_input := st.chat_input("数学の質問を入力してください…"):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.rerun()

    # 未回答メッセージがあればAPI呼び出し
    history = st.session_state.chat_history
    if history and history[-1]["role"] == "user":
        _call_ai()


def _call_ai():
    history = st.session_state.chat_history
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    with st.chat_message("assistant"):
        with st.spinner("考えています…"):
            if not api_key:
                reply = (
                    "申し訳ありません。ANTHROPIC_API_KEY が設定されていないため回答できません。\n\n"
                    "環境変数 `ANTHROPIC_API_KEY` を設定してから再起動してください。"
                )
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                return

            try:
                client = anthropic.Anthropic(api_key=api_key)

                # プロンプトキャッシュ付きのメッセージ構築
                messages = []
                for i, msg in enumerate(history):
                    content = msg["content"]
                    # システムプロンプトはシステムフィールドで渡すため、
                    # 最初の数ターンにキャッシュ制御を付与
                    if i == 0 and msg["role"] == "user":
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": content,
                                    "cache_control": {"type": "ephemeral"},
                                }
                            ],
                        })
                    else:
                        messages.append({"role": msg["role"], "content": content})

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=[
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=messages,
                )
                reply = response.content[0].text
            except anthropic.APIStatusError as e:
                reply = f"APIエラーが発生しました: {e.message}"
            except Exception as e:
                reply = f"エラーが発生しました: {str(e)}"

            st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})


    # 履歴クリアボタン
    if st.session_state.chat_history:
        if st.button("🗑️ 会話をリセット", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ──────────────────────────────────────────────
# メインルーター
# ──────────────────────────────────────────────
def main():
    render_sidebar()

    page = st.session_state.page
    if page == "home":
        render_home()
    elif page == "unit":
        render_unit()
    elif page == "quiz":
        render_quiz()
    elif page == "chat":
        render_chat()
    else:
        render_home()


if __name__ == "__main__":
    main()
