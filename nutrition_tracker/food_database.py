"""食品栄養データベース（CSVベース、手動入力のフォールバック用）"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .models import NutritionInfo

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "food_database.csv"


@dataclass
class FoodRecord:
    """100gあたりの食品データ"""

    name: str
    category: str
    nutrition_per_100g: NutritionInfo


class FoodDatabase:
    """CSVファイルから食品の栄養データを読み込み、検索する"""

    def __init__(self, csv_path: str | Path = DEFAULT_DB_PATH):
        self.csv_path = Path(csv_path)
        self._records: list[FoodRecord] = []
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"食品データベースが見つかりません: {self.csv_path}")

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nutrition = NutritionInfo(
                    calories=float(row["calories"]),
                    protein=float(row["protein"]),
                    fat=float(row["fat"]),
                    carbohydrates=float(row["carbohydrates"]),
                    sugar=float(row["sugar"]),
                    fiber=float(row["fiber"]),
                    salt=float(row["salt"]),
                )
                self._records.append(
                    FoodRecord(
                        name=row["name"],
                        category=row["category"],
                        nutrition_per_100g=nutrition,
                    )
                )

    @property
    def all_records(self) -> list[FoodRecord]:
        return list(self._records)

    @property
    def categories(self) -> list[str]:
        seen = []
        for r in self._records:
            if r.category not in seen:
                seen.append(r.category)
        return seen

    def search(self, query: str) -> list[FoodRecord]:
        """食品名の部分一致検索（大文字小文字を区別しない）"""
        if not query:
            return self.all_records
        q = query.lower()
        return [r for r in self._records if q in r.name.lower()]

    def find_exact(self, name: str) -> FoodRecord | None:
        for r in self._records:
            if r.name == name:
                return r
        return None
