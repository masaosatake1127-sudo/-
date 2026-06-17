"""日次・期間集計と目標達成度の計算"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_type

from .models import DailyGoal, FoodEntry, NutritionInfo


@dataclass
class DailySummary:
    target_date: date_type
    total: NutritionInfo
    entries: list[FoodEntry]
    goal: DailyGoal

    @property
    def calories_ratio(self) -> float:
        return _ratio(self.total.calories, self.goal.calories)

    @property
    def protein_ratio(self) -> float:
        return _ratio(self.total.protein, self.goal.protein)

    @property
    def fat_ratio(self) -> float:
        return _ratio(self.total.fat, self.goal.fat)

    @property
    def carbohydrates_ratio(self) -> float:
        return _ratio(self.total.carbohydrates, self.goal.carbohydrates)

    @property
    def salt_ratio(self) -> float:
        return _ratio(self.total.salt, self.goal.salt)


def _ratio(value: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return value / target * 100.0


def sum_nutrition(entries: list[FoodEntry]) -> NutritionInfo:
    total = NutritionInfo()
    for entry in entries:
        total = total + entry.nutrition
    return total


def summarize_day(
    target_date: date_type, entries: list[FoodEntry], goal: DailyGoal
) -> DailySummary:
    return DailySummary(
        target_date=target_date,
        total=sum_nutrition(entries),
        entries=entries,
        goal=goal,
    )


def summarize_by_meal(entries: list[FoodEntry]) -> dict[str, NutritionInfo]:
    result: dict[str, NutritionInfo] = {}
    for entry in entries:
        result[entry.meal_type] = result.get(entry.meal_type, NutritionInfo()) + entry.nutrition
    return result


def daily_totals_in_range(
    entries: list[FoodEntry],
) -> dict[date_type, NutritionInfo]:
    """日付ごとの合計栄養素を計算する（履歴グラフ用）"""
    totals: dict[date_type, NutritionInfo] = {}
    for entry in entries:
        totals[entry.entry_date] = totals.get(entry.entry_date, NutritionInfo()) + entry.nutrition
    return totals
