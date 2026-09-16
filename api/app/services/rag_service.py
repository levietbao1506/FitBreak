# IMPORT & CALL FUNCTION #
import json, re, asyncio
from pathlib import Path
from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field

from app.core.exceptions import (
    InvalidResponseError,
    InvalidUserInformationError,
    NoMatchingFoodsError,
)
from app.core.ollama_client import generate_chat
from app.services.prompt_builder import prompt_builder
#####

# DATABASE #
DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "dataset" / "Vietnamese_Food_Database.csv"
DF_FOODS = pd.read_csv(DATA_PATH)
DF_FOODS["allergens"] = DF_FOODS["allergens"].fillna("")

# Dùng cơm trắng 100g làm chuẩn tính toán calo/protein/giá
RICE_NUTRIENTS_PER_100G = {"calories": 130, "protein": 2.7, "price": 2000}


def get_user_value(user_information: dict, field: str, default=None):
      if isinstance(user_information, dict):
            return user_information.get(field, default)
      return getattr(user_information, field, default)


def _normalize_diet_key(value) -> str:
    return re.sub(r"[\s_\-]+", "", str(value).strip().lower())


def filter_foods(df: pd.DataFrame, user_diet: str, user_allergens) -> pd.DataFrame:
      if isinstance(user_allergens, str):
            user_allergens = [
                  a.strip().lower() for a in user_allergens.replace(",", ";").split(";") if a.strip()
            ]
      else:
            user_allergens = [
                  a.strip().lower() for a in (user_allergens or []) if a and a.strip()
            ]

      def has_allergen(item_allergens):
            if not item_allergens:
                  return False
            item_list = [a.strip().lower() for a in str(item_allergens).split(";")]
            return any(a in user_allergens for a in item_list)

      # 1. Lọc dị ứng
      valid_df = df[~df["allergens"].apply(has_allergen)].copy()

      # 2. Lọc chế độ ăn
      if user_diet:
        norm_user_diet = _normalize_diet_key(user_diet)
        valid_df = valid_df[
            valid_df["diet_type"].apply(
                lambda diets: norm_user_diet in {
                    _normalize_diet_key(d) for d in str(diets).split(";")
                }
            )
        ]

      return valid_df


import unicodedata

def normalize_text(text: str) -> str:
      return unicodedata.normalize("NFC", str(text).strip().lower())

def get_dish_info(dish_name: str, df: pd.DataFrame) -> dict:
      """Helper tra cứu thông tin dinh dưỡng an toàn từ tên món."""
      norm_target = normalize_text(dish_name)
      
      # 1. Khớp chính xác 100% (sau khi chuẩn hóa Unicode & lowercase)
      matched = df[df["name"].apply(normalize_text) == norm_target]
      
      # 2. Nếu không khớp chính xác, thử tìm kiếm chuỗi con (fallback)
      if matched.empty:
            matched = df[df["name"].apply(normalize_text).str.contains(norm_target, regex=False)]
            
      # 3. Nếu vẫn không có, lấy món đầu tiên của danh sách để tránh crash (chống hallucination mạnh)
      if matched.empty and not df.empty:
            matched = df.head(1)
            
      if not matched.empty:
            row = matched.iloc[0]
            ingredients_val = row.get("ingredients", row["name"])
            return {
                  "calories": float(row.get("calories", 0)),
                  "protein": float(row.get("protein_g", 0)),
                  "price": float(row.get("cost_vnd", 0)),
                  "ingredients": str(ingredients_val) if pd.notna(ingredients_val) else row["name"],
                  "real_name": row["name"]
            }
      raise InvalidResponseError(f"Món ăn không có trong database: {dish_name}")
#####

# PARSE DISH #
class Breakfast(BaseModel):
      dish_name: str

class MainMeal(BaseModel):
      main_dish: str
      rice_grams: int = Field(default=0, ge=0, le=300, description="Số gram cơm (tối đa 300g)")

class MealsPlan(BaseModel):
      breakfast: Breakfast
      lunch: MainMeal
      dinner: MainMeal

class LLMMealResponse(BaseModel):
      estimated_total_cost: Optional[float] = 0
      meals: MealsPlan


def parse_llm_meal_response(raw_text: str) -> LLMMealResponse:
      match = re.search(r"\{[\s\S]*\}", raw_text)
      if not match:
            raise InvalidResponseError("LLM không trả về JSON hợp lệ")
      try:
            data = json.loads(match.group(0))
            return LLMMealResponse(**data)
      except Exception as e:
            raise InvalidResponseError(f"Không thể parse JSON từ LLM: {str(e)}")


def validate_user_information(user_information: dict) -> None:
      required_fields = ("calories_need", "daily_budget", "protein_need", "aim", "diet_type")
      missing_fields = [
            field for field in required_fields if get_user_value(user_information, field) is None
      ]
      if missing_fields:
            raise InvalidUserInformationError(
                  f"Thiếu thông tin người dùng: {', '.join(missing_fields)}"
            )

      numeric_fields = ("calories_need", "daily_budget", "protein_need")
      for field in numeric_fields:
            value = get_user_value(user_information, field)
            if not isinstance(value, (int, float)) or value < 0:
                  raise InvalidUserInformationError(f"{field} phải là số không âm")


def format_meal_summary(response: str, df_pool: pd.DataFrame, user_information: dict) -> dict:
      meal_plan = parse_llm_meal_response(response)

      # 1. Bữa sáng
      bf_name_llm = meal_plan.meals.breakfast.dish_name
      bf_info = get_dish_info(bf_name_llm, df_pool)

      # 2. Bữa trưa
      lu = meal_plan.meals.lunch
      lu_main = get_dish_info(lu.main_dish, df_pool)
      lu_rice_cal = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
      lu_rice_pro = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
      lu_rice_cost = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]
      lu_total_cal = lu_main["calories"] + lu_rice_cal
      lu_total_pro = lu_main["protein"] + lu_rice_pro
      lu_total_cost = lu_main["price"] + lu_rice_cost

      # 3. Bữa tối
      dn = meal_plan.meals.dinner
      dn_main = get_dish_info(dn.main_dish, df_pool)
      dn_rice_cal = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
      dn_rice_pro = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
      dn_rice_cost = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]
      dn_total_cal = dn_main["calories"] + dn_rice_cal
      dn_total_pro = dn_main["protein"] + dn_rice_pro
      dn_total_cost = dn_main["price"] + dn_rice_cost

      # Tổng kết
      total_cal = bf_info["calories"] + lu_total_cal + dn_total_cal
      total_pro = bf_info["protein"] + lu_total_pro + dn_total_pro
      total_cost = bf_info["price"] + lu_total_cost + dn_total_cost

      return {
            "total_calories": round(total_cal),
            "total_protein": round(total_pro, 1),
            "total_cost": round(total_cost),
            "meals": [
                  {
                        "type": "Bữa sáng",
                        "time": "07:00",
                        "name": bf_info["real_name"],
                        "desc": "",
                        "kcal": round(bf_info["calories"]),
                        "cost": round(bf_info["price"]),
                        "protein": round(bf_info["protein"], 1),
                        "carbs": 0,
                        "fat": 0,
                        "ingredients": bf_info["ingredients"],
                  },
                  {
                        "type": "Bữa trưa",
                        "time": "12:00",
                        "name": f'{lu_main["real_name"]} + {lu.rice_grams}g cơm',
                        "desc": "",
                        "kcal": round(lu_total_cal),
                        "cost": round(lu_total_cost),
                        "protein": round(lu_total_pro, 1),
                        "carbs": 0,
                        "fat": 0,
                        "ingredients": lu_main["ingredients"],
                  },
                  {
                        "type": "Bữa tối",
                        "time": "19:00",
                        "name": f'{dn_main["real_name"]} + {dn.rice_grams}g cơm',
                        "desc": "",
                        "kcal": round(dn_total_cal),
                        "cost": round(dn_total_cost),
                        "protein": round(dn_total_pro, 1),
                        "carbs": 0,
                        "fat": 0,
                        "ingredients": dn_main["ingredients"],
                  },
            ],
      }

# MAIN RAG #
async def process_rag_pipeline(user_information: dict) -> str:
      validate_user_information(user_information)

      diet_type = get_user_value(user_information, "diet_type")
      allergen = get_user_value(user_information, "allergen", "")

      # Retrieval: Lọc danh sách món hợp lệ từ CSV
      filtered_df = filter_foods(DF_FOODS, diet_type, allergen)
      if filtered_df.empty:
            raise NoMatchingFoodsError("Không tìm thấy món ăn phù hợp với chế độ ăn và dị ứng.")

      # Truyền filtered_df vào prompt_builder để LLM chỉ chọn trong danh sách này
      prompt = await prompt_builder(
            calories_need=get_user_value(user_information, "calories_need"),
            daily_budget=get_user_value(user_information, "daily_budget"),
            protein_need=get_user_value(user_information, "protein_need"),
            aim=get_user_value(user_information, "aim"),
            diet_type=diet_type,
            allergen=allergen,
            filtered_food=filtered_df,
      )

      response = await generate_chat(prompt, response_format=LLMMealResponse.model_json_schema())
      return format_meal_summary(response, filtered_df, user_information)

async def main():
      user_information = {
            "calories_need": 2000,
            "protein_need": 110,
            "daily_budget": 120000,
            "aim": "Tăng cơ",
            "diet_type": "home_cooked",
            "allergen": "seafood"
      }
      
      result = await process_rag_pipeline(user_information)
      print(result)

if __name__ == "__main__":
      asyncio.run(main())