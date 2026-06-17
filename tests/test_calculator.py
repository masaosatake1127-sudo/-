from datetime import date

from nutrition_tracker.calculator import (
    daily_totals_in_range,
    summarize_by_meal,
    summarize_day,
    sum_nutrition,
)
from nutrition_tracker.models import DailyGoal, FoodEntry, NutritionInfo


def _entry(meal_type, calories, entry_date=None):
    return FoodEntry(
        food_name="テスト食品",
        nutrition=NutritionInfo(calories=calories, protein=10, fat=5, carbohydrates=20, salt=1),
        meal_type=meal_type,
        entry_date=entry_date or date(2026, 1, 1),
    )


def test_sum_nutrition_empty():
    total = sum_nutrition([])
    assert total.calories == 0.0


def test_sum_nutrition():
    entries = [_entry("朝食", 100), _entry("昼食", 200)]
    total = sum_nutrition(entries)
    assert total.calories == 300


def test_summarize_day_ratios():
    entries = [_entry("朝食", 500)]
    goal = DailyGoal(calories=1000, protein=50, fat=30, carbohydrates=100, salt=5)
    summary = summarize_day(date(2026, 1, 1), entries, goal)
    assert summary.total.calories == 500
    assert summary.calories_ratio == 50.0


def test_summarize_day_zero_goal_no_division_error():
    goal = DailyGoal(calories=0, protein=0, fat=0, carbohydrates=0, salt=0)
    summary = summarize_day(date(2026, 1, 1), [], goal)
    assert summary.calories_ratio == 0.0


def test_summarize_by_meal():
    entries = [_entry("朝食", 100), _entry("朝食", 50), _entry("昼食", 200)]
    by_meal = summarize_by_meal(entries)
    assert by_meal["朝食"].calories == 150
    assert by_meal["昼食"].calories == 200


def test_daily_totals_in_range():
    entries = [
        _entry("朝食", 100, entry_date=date(2026, 1, 1)),
        _entry("昼食", 200, entry_date=date(2026, 1, 1)),
        _entry("夕食", 300, entry_date=date(2026, 1, 2)),
    ]
    totals = daily_totals_in_range(entries)
    assert totals[date(2026, 1, 1)].calories == 300
    assert totals[date(2026, 1, 2)].calories == 300
