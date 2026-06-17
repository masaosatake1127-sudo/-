from datetime import date

from nutrition_tracker.models import DailyGoal, FoodEntry, NutritionInfo


def test_nutrition_info_defaults_to_zero():
    n = NutritionInfo()
    assert n.calories == 0.0
    assert n.protein == 0.0


def test_nutrition_info_add():
    a = NutritionInfo(calories=100, protein=10, fat=5, carbohydrates=20, sugar=5, fiber=2, salt=1)
    b = NutritionInfo(calories=50, protein=5, fat=2, carbohydrates=10, sugar=2, fiber=1, salt=0.5)
    total = a + b
    assert total.calories == 150
    assert total.protein == 15
    assert total.fat == 7
    assert total.carbohydrates == 30
    assert total.salt == 1.5


def test_nutrition_info_scaled():
    n = NutritionInfo(calories=200, protein=20, fat=10, carbohydrates=30, sugar=5, fiber=2, salt=1)
    scaled = n.scaled(0.5)
    assert scaled.calories == 100
    assert scaled.protein == 10
    assert scaled.salt == 0.5


def test_food_entry_defaults():
    entry = FoodEntry(food_name="白米", nutrition=NutritionInfo(calories=168))
    assert entry.meal_type == "間食"
    assert entry.source == "manual"
    assert entry.entry_date == date.today()
    assert entry.entry_id is None


def test_daily_goal_defaults():
    goal = DailyGoal()
    assert goal.calories == 2000.0
    assert goal.protein == 60.0
