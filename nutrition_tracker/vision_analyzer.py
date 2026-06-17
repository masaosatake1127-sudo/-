"""Claude Vision APIを使った食事写真の解析

ANTHROPIC_API_KEY が設定されている場合のみ利用可能。
未設定の場合は呼び出し側が手動入力（food_database）にフォールバックする。
"""

from __future__ import annotations

import base64
import os
from typing import List

from pydantic import BaseModel

from .models import NutritionInfo

MODEL_ID = "claude-opus-4-8"

_EXT_TO_MEDIA_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

SYSTEM_PROMPT = (
    "あなたは栄養士です。提供された食事の写真を見て、写っている食品・料理を識別し、"
    "それぞれの推定量(グラム)と栄養成分を見積もってください。"
    "日本の一般的な食事を前提に、写真に写っているすべての食品項目を個別にリストアップし、"
    "妥当な範囲で現実的な数値を推定してください。不明な場合は一般的な標準量で見積もってください。"
)


class FoodItemEstimate(BaseModel):
    name: str
    quantity_g: float
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    sugar: float
    fiber: float
    salt: float


class PhotoAnalysisResult(BaseModel):
    items: List[FoodItemEstimate]
    summary: str


class VisionAnalyzerError(Exception):
    """写真解析中に発生したエラー"""


def is_available() -> bool:
    """ANTHROPIC_API_KEY が設定されているか（AI解析が使えるか）"""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _media_type_for(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _EXT_TO_MEDIA_TYPE.get(ext, "image/jpeg")


def analyze_photo(image_bytes: bytes, filename: str = "photo.jpg") -> PhotoAnalysisResult:
    """食事の写真を解析し、食品項目ごとの栄養推定値を返す

    ANTHROPIC_API_KEY が設定されていない場合は VisionAnalyzerError を送出する。
    """
    if not is_available():
        raise VisionAnalyzerError(
            "ANTHROPIC_API_KEY が設定されていません。手動入力をご利用ください。"
        )

    import anthropic

    client = anthropic.Anthropic()
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    media_type = _media_type_for(filename)

    try:
        response = client.messages.parse(
            model=MODEL_ID,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "この写真の食事内容を分析し、食品項目ごとの名称、推定量(g)、"
                                "カロリー(kcal)、たんぱく質(g)、脂質(g)、炭水化物(g)、糖質(g)、"
                                "食物繊維(g)、塩分(g)を見積もってください。"
                            ),
                        },
                    ],
                }
            ],
            output_format=PhotoAnalysisResult,
        )
    except anthropic.AuthenticationError as e:
        raise VisionAnalyzerError(f"APIキーが無効です: {e}") from e
    except anthropic.PermissionDeniedError as e:
        raise VisionAnalyzerError(f"APIキーに権限がありません: {e}") from e
    except anthropic.RateLimitError as e:
        raise VisionAnalyzerError(f"レート制限に達しました。しばらくしてから再試行してください: {e}") from e
    except anthropic.APIConnectionError as e:
        raise VisionAnalyzerError(f"ネットワークエラーが発生しました: {e}") from e
    except anthropic.APIStatusError as e:
        raise VisionAnalyzerError(f"APIエラーが発生しました ({e.status_code}): {e.message}") from e

    if response.parsed_output is None:
        raise VisionAnalyzerError("写真の解析結果を取得できませんでした。")

    return response.parsed_output


def estimate_to_nutrition(item: FoodItemEstimate) -> NutritionInfo:
    return NutritionInfo(
        calories=item.calories,
        protein=item.protein,
        fat=item.fat,
        carbohydrates=item.carbohydrates,
        sugar=item.sugar,
        fiber=item.fiber,
        salt=item.salt,
    )
