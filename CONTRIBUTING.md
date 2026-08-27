# コンテンツ追加ガイド

このドキュメントでは **単元の追加** と **練習問題の追加** を差分（パッチ）で行う手順を説明します。

---

## 目次

1. [ファイルの役割](#ファイルの役割)
2. [練習問題を追加する](#練習問題を追加する)
3. [新しい単元を追加する](#新しい単元を追加する)
4. [差分（パッチ）の作り方と適用](#差分パッチの作り方と適用)
5. [データ構造リファレンス](#データ構造リファレンス)

---

## ファイルの役割

| ファイル | 変更内容 |
|---------|---------|
| `math_content/problems.py` | 練習問題・解答・解説の追加 |
| `math_content/curriculum.py` | 単元説明・重要公式の追加 |
| `math_tutor_app.py` | 画面ロジック（通常は変更不要） |

---

## 練習問題を追加する

### 手順

`math_content/problems.py` の対象単元キーのリストに辞書を追加します。

```
単元キー一覧:
  poly_calc      → 式の計算
  simultaneous   → 連立方程式
  linear_func    → 一次関数
  geometry       → 図形の性質
  probability    → 確率
```

### 差分の例 — 「確率」に問題を1問追加

```diff
--- a/math_content/problems.py
+++ b/math_content/problems.py
@@ -末尾付近（probability リスト内）@@ 
         "level": 2,
     },
+    {
+        "id": "prob5",
+        "question": "52枚のトランプから1枚引くとき、ハートの絵札（J・Q・K）が出る確率を求めなさい。",
+        "type": "choice",
+        "choices": ["3/52", "1/4", "3/13", "1/13"],
+        "answer": "3/13",
+        "solution": """全体の場合の数: 52通り
+ハートの絵札（J・Q・K）: 3通り
+
+$$P = \\frac{3}{52}$$
+
+約分すると $\\dfrac{3}{52}$ はこれ以上約分できないが、
+選択肢の $\\dfrac{3}{13}$ は…？ → 問題文の「52枚から1枚」に注意！
+正解は $\\dfrac{3}{52}$ です。
+""",
+        "level": 2,
+    },
 ]
```

### パッチの適用

```bash
# パッチファイルとして保存した場合
git apply add_prob5.patch

# 直接編集した場合はそのままコミット
git add math_content/problems.py
git commit -m "問題追加: 確率 prob5（トランプの絵札）"
```

---

## 新しい単元を追加する

新単元（例: **データの活用**）を追加するには **2ファイル** を編集します。

### ① `math_content/curriculum.py` に単元を追加

```diff
--- a/math_content/curriculum.py
+++ b/math_content/curriculum.py
@@ -UNITS リスト末尾 @@
     },  # ← 確率ブロックの閉じ括弧
+    {
+        "id": "data_analysis",
+        "title": "データの活用",
+        "icon": "📊",
+        "description": "度数分布・平均・中央値・最頻値・箱ひげ図を学びます。",
+        "sections": [
+            {
+                "name": "代表値",
+                "explanation": """
+**平均値**: すべての値の合計 ÷ 個数
+
+**中央値（メジアン）**: データを大きさ順に並べたときの中央の値
+- 個数が偶数のとき → 中央2つの平均
+
+**最頻値（モード）**: 最も多く出てくる値
+""",
+            },
+        ],
+        "key_formulas": [
+            {
+                "formula": "\\text{平均値} = \\frac{\\text{合計}}{\\text{個数}}",
+                "label": "平均値",
+            },
+        ],
+    },
 ]
```

### ② `math_content/problems.py` に問題を追加

```diff
--- a/math_content/problems.py
+++ b/math_content/problems.py
@@ -PROBLEMS 辞書末尾 @@
     ],  # ← probability リストの閉じ括弧
+    "data_analysis": [
+        {
+            "id": "da1",
+            "question": "データ {3, 5, 7, 7, 8} の平均値を求めなさい。",
+            "type": "choice",
+            "choices": ["6", "7", "6.5", "5"],
+            "answer": "6",
+            "solution": """平均値 $= \\dfrac{3+5+7+7+8}{5} = \\dfrac{30}{5} = 6$""",
+            "level": 1,
+        },
+    ],
 }
```

---

## 差分（パッチ）の作り方と適用

### パッチを作る

```bash
# 編集後にパッチファイルを生成
git diff math_content/problems.py > add_problems.patch

# ステージ済みの変更からパッチを生成
git diff --cached math_content/ > math_content.patch
```

### パッチを確認する

```bash
# 差分の内容を確認（適用前）
git apply --check add_problems.patch
```

### パッチを適用する

```bash
# 適用
git apply add_problems.patch

# 逆適用（取り消し）
git apply --reverse add_problems.patch
```

### コミット & プッシュ

```bash
git add math_content/
git commit -m "単元追加: データの活用 / 問題3問"
git push -u origin <ブランチ名>
```

---

## データ構造リファレンス

### 単元 (`curriculum.py` の `UNITS` リスト)

```python
{
    "id":          str,          # 一意のキー（例: "poly_calc"）
    "title":       str,          # 表示名（例: "式の計算"）
    "icon":        str,          # 絵文字アイコン（例: "🔢"）
    "description": str,          # 単元の短い説明
    "sections": [                # セクションリスト（タブになる）
        {
            "name":        str,  # タブ名
            "explanation": str,  # 説明文（Markdown + LaTeX 可）
        },
        ...
    ],
    "key_formulas": [            # 重要公式リスト
        {
            "formula": str,      # LaTeX 式（$ 不要、raw string 推奨）
            "label":   str,      # 公式の名前
        },
        ...
    ],
}
```

### 問題 (`problems.py` の `PROBLEMS` 辞書)

```python
"<unit_id>": [
    {
        "id":       str,         # 一意のID（例: "pc1"）
        "question": str,         # 問題文（Markdown + LaTeX 可）
        "type":     "choice",    # 現在は "choice" のみ対応
        "choices":  list[str],   # 選択肢（4つ推奨）
        "answer":   str,         # 正解（choices の中の1つと完全一致）
        "solution": str,         # 解説（Markdown + LaTeX 可）
        "level":    int,         # 難易度: 1=基本 / 2=標準 / 3=応用
    },
    ...
]
```

### LaTeX 記法のヒント

| 用途 | 書き方 |
|------|--------|
| インライン数式 | `` `$a + b$` `` |
| ブロック数式 | `` `$$\frac{a}{b}$$` `` |
| 分数 | `\frac{分子}{分母}` |
| 累乗 | `x^{2}` |
| 連立方程式 | `\begin{cases} ... \\ ... \end{cases}` |
| バックスラッシュ | Python 文字列中は `\\frac` と二重にする |
