"""栄養トラッカー - ドメインモデル"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as date_type
from datetime import datetime


MEAL_TYPES = ["朝食", "昼食", "夕食", "間食"]


@dataclass
class NutritionInfo:
    """100gあたり、または1食あたりの栄養成分"""

    calories: float = 0.0
    protein: float = 0.0
    fat: float = 0.0
    carbohydrates: float = 0.0
    sugar: float = 0.0
    fiber: float = 0.0
    salt: float = 0.0

    def scaled(self, factor: float) -> "NutritionInfo":
        return NutritionInfo(
            calories=self.calories * factor,
            protein=self.protein * factor,
            fat=self.fat * factor,
            carbohydrates=self.carbohydrates * factor,
            sugar=self.sugar * factor,
            fiber=self.fiber * factor,
            salt=self.salt * factor,
        )

    def __add__(self, other: "NutritionInfo") -> "NutritionInfo":
        return NutritionInfo(
            calories=self.calories + other.calories,
            protein=self.protein + other.protein,
            fat=self.fat + other.fat,
            carbohydrates=self.carbohydrates + other.carbohydrates,
            sugar=self.sugar + other.sugar,
            fiber=self.fiber + other.fiber,
            salt=self.salt + other.salt,
        )


@dataclass
class FoodEntry:
    """1件の食事記録"""

    food_name: str
    nutrition: NutritionInfo
    meal_type: str = "間食"
    quantity_g: float = 0.0
    entry_date: date_type = field(default_factory=date_type.today)
    source: str = "manual"  # "ai" or "manual"
    photo_path: str | None = None
    note: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    entry_id: int | None = None


@dataclass
class DailyGoal:
    """1日あたりの栄養目標値"""

    calories: float = 2000.0
    protein: float = 60.0
    fat: float = 60.0
    carbohydrates: float = 250.0
    salt: float = 7.5
