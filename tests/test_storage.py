from datetime import date

import pytest

from nutrition_tracker.models import DailyGoal, FoodEntry, NutritionInfo
from nutrition_tracker.storage import NutritionStorage


@pytest.fixture()
def storage(tmp_path):
    return NutritionStorage(db_path=tmp_path / "test_nutrition.db")


def test_add_and_get_entry(storage):
    entry = FoodEntry(
        food_name="白米",
        nutrition=NutritionInfo(calories=168, protein=2.5),
        meal_type="朝食",
        quantity_g=100,
        entry_date=date(2026, 1, 1),
    )
    entry_id = storage.add_entry(entry)
    assert entry_id is not None

    entries = storage.get_entries_by_date(date(2026, 1, 1))
    assert len(entries) == 1
    assert entries[0].food_name == "白米"
    assert entries[0].nutrition.calories == 168
    assert entries[0].entry_id == entry_id


def test_get_entries_in_range(storage):
    storage.add_entry(
        FoodEntry(food_name="A", nutrition=NutritionInfo(calories=100), entry_date=date(2026, 1, 1))
    )
    storage.add_entry(
        FoodEntry(food_name="B", nutrition=NutritionInfo(calories=200), entry_date=date(2026, 1, 5))
    )
    storage.add_entry(
        FoodEntry(food_name="C", nutrition=NutritionInfo(calories=300), entry_date=date(2026, 1, 10))
    )

    entries = storage.get_entries_in_range(date(2026, 1, 1), date(2026, 1, 5))
    names = {e.food_name for e in entries}
    assert names == {"A", "B"}


def test_delete_entry(storage):
    entry_id = storage.add_entry(
        FoodEntry(food_name="削除対象", nutrition=NutritionInfo(calories=100), entry_date=date(2026, 1, 1))
    )
    storage.delete_entry(entry_id)
    assert storage.get_entries_by_date(date(2026, 1, 1)) == []


def test_goal_defaults_when_unset(storage):
    goal = storage.get_goal()
    assert goal == DailyGoal()


def test_save_and_get_goal(storage):
    goal = DailyGoal(calories=2200, protein=80, fat=70, carbohydrates=280, salt=6.0)
    storage.save_goal(goal)
    loaded = storage.get_goal()
    assert loaded == goal


def test_save_goal_overwrites(storage):
    storage.save_goal(DailyGoal(calories=2000))
    storage.save_goal(DailyGoal(calories=2500))
    assert storage.get_goal().calories == 2500
