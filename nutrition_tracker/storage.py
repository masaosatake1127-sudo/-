"""SQLiteによる食事記録・目標値の永続化"""

from __future__ import annotations

import sqlite3
from datetime import date as date_type
from datetime import datetime
from pathlib import Path

from .models import DailyGoal, FoodEntry, NutritionInfo

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrition.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS food_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    food_name TEXT NOT NULL,
    quantity_g REAL NOT NULL,
    calories REAL NOT NULL,
    protein REAL NOT NULL,
    fat REAL NOT NULL,
    carbohydrates REAL NOT NULL,
    sugar REAL NOT NULL,
    fiber REAL NOT NULL,
    salt REAL NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual',
    photo_path TEXT,
    note TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_goal (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    calories REAL NOT NULL,
    protein REAL NOT NULL,
    fat REAL NOT NULL,
    carbohydrates REAL NOT NULL,
    salt REAL NOT NULL
);
"""


class NutritionStorage:
    """食事記録と目標値のCRUDを行う"""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    # ── 食事記録 ──────────────────────────────

    def add_entry(self, entry: FoodEntry) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO food_entries
                    (entry_date, meal_type, food_name, quantity_g,
                     calories, protein, fat, carbohydrates, sugar, fiber, salt,
                     source, photo_path, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.entry_date.isoformat(),
                    entry.meal_type,
                    entry.food_name,
                    entry.quantity_g,
                    entry.nutrition.calories,
                    entry.nutrition.protein,
                    entry.nutrition.fat,
                    entry.nutrition.carbohydrates,
                    entry.nutrition.sugar,
                    entry.nutrition.fiber,
                    entry.nutrition.salt,
                    entry.source,
                    entry.photo_path,
                    entry.note,
                    entry.created_at.isoformat(),
                ),
            )
            return cur.lastrowid

    def delete_entry(self, entry_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM food_entries WHERE entry_id = ?", (entry_id,))

    def get_entries_by_date(self, target_date: date_type) -> list[FoodEntry]:
        return self.get_entries_in_range(target_date, target_date)

    def get_entries_in_range(
        self, start_date: date_type, end_date: date_type
    ) -> list[FoodEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM food_entries
                WHERE entry_date BETWEEN ? AND ?
                ORDER BY entry_date ASC, created_at ASC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> FoodEntry:
        return FoodEntry(
            entry_id=row["entry_id"],
            entry_date=date_type.fromisoformat(row["entry_date"]),
            meal_type=row["meal_type"],
            food_name=row["food_name"],
            quantity_g=row["quantity_g"],
            nutrition=NutritionInfo(
                calories=row["calories"],
                protein=row["protein"],
                fat=row["fat"],
                carbohydrates=row["carbohydrates"],
                sugar=row["sugar"],
                fiber=row["fiber"],
                salt=row["salt"],
            ),
            source=row["source"],
            photo_path=row["photo_path"],
            note=row["note"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    # ── 目標値 ──────────────────────────────

    def get_goal(self) -> DailyGoal:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM daily_goal WHERE id = 1").fetchone()
        if row is None:
            return DailyGoal()
        return DailyGoal(
            calories=row["calories"],
            protein=row["protein"],
            fat=row["fat"],
            carbohydrates=row["carbohydrates"],
            salt=row["salt"],
        )

    def save_goal(self, goal: DailyGoal) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_goal (id, calories, protein, fat, carbohydrates, salt)
                VALUES (1, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    calories = excluded.calories,
                    protein = excluded.protein,
                    fat = excluded.fat,
                    carbohydrates = excluded.carbohydrates,
                    salt = excluded.salt
                """,
                (goal.calories, goal.protein, goal.fat, goal.carbohydrates, goal.salt),
            )
