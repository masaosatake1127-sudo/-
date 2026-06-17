"""栄養トラッカー - 食事写真から栄養素を記録・分析するパッケージ"""

from .calculator import DailySummary, daily_totals_in_range, summarize_by_meal, summarize_day
from .food_database import FoodDatabase, FoodRecord
from .models import MEAL_TYPES, DailyGoal, FoodEntry, NutritionInfo
from .storage import NutritionStorage
from .vision_analyzer import (
    FoodItemEstimate,
    PhotoAnalysisResult,
    VisionAnalyzerError,
    analyze_photo,
    estimate_to_nutrition,
    is_available as vision_is_available,
)

__all__ = [
    "DailySummary",
    "daily_totals_in_range",
    "summarize_by_meal",
    "summarize_day",
    "FoodDatabase",
    "FoodRecord",
    "MEAL_TYPES",
    "DailyGoal",
    "FoodEntry",
    "NutritionInfo",
    "NutritionStorage",
    "FoodItemEstimate",
    "PhotoAnalysisResult",
    "VisionAnalyzerError",
    "analyze_photo",
    "estimate_to_nutrition",
    "vision_is_available",
]
