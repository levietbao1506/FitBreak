# IMPORT & CALL FUNCTION #
import json, re, asyncio
from pathlib import Path
from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field

from api.app.core.exceptions import (
    InvalidResponseError,
    InvalidUserInformationError,
    NoMatchingFoodsError,
)
from api.app.core.ollama_client import generate_chat
from api.app.services.prompt_builder import prompt_builder
#####

# DATABASE #
DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "Vietnamese_Food_Database.csv"
DF_FOODS = pd.read_csv(DATA_PATH)
DF_FOODS["allergens"] = DF_FOODS["allergens"].fillna("")

# Dùng cơm trắng 100g làm chuẩn tính toán calo/protein/giá
RICE_NUTRIENTS_PER_100G = {"calories": 130, "protein": 2.7, "price": 2000}


def get_user_value(user_information: dict, field: str, default=None):
      if isinstance(user_information, dict):
            return user_information.get(field, default)
      return getattr(user_information, field, default)


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
            normalized_diet = str(user_diet).strip().lower()
            valid_df = valid_df[
                  valid_df["diet_type"].apply(
                  lambda diets: normalized_diet
                  in {diet.strip().lower() for diet in str(diets).split(";")}
                  )
            ]

      return valid_df


def get_dish_info(dish_name: str, df: pd.DataFrame) -> dict:
      """Helper tra cứu thông tin dinh dưỡng an toàn từ tên món."""
      matched = df[df["name"].str.strip().str.lower() == dish_name.strip().lower()]
      if not matched.empty:
            row = matched.iloc[0]
            ingredients_val = row.get("ingredients", dish_name)
            return {
                  "calories": float(row.get("calories", 0)),
                  "protein": float(row.get("protein_g", 0)),
                  "price": float(row.get("cost_vnd", 0)),
                  "ingredients": str(ingredients_val) if pd.notna(ingredients_val) else dish_name,
            }
      raise InvalidResponseError(f"Món ăn không có trong database: {dish_name}")
#####

# PARSE DISH #
class Breakfast(BaseModel):
      dish_name: str

class MainMeal(BaseModel):
      main_dish: str
      side_dish: str
      rice_grams: int = Field(default=0, ge=0, description="Số gram cơm")

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


def format_meal_summary(response: str, df_pool: pd.DataFrame, user_information: dict) -> str:
      meal_plan = parse_llm_meal_response(response)

      # 1. Bữa sáng
      bf_name = meal_plan.meals.breakfast.dish_name
      bf_info = get_dish_info(bf_name, df_pool)

      # 2. Bữa trưa
      lu = meal_plan.meals.lunch
      lu_main = get_dish_info(lu.main_dish, df_pool)
      lu_side = get_dish_info(lu.side_dish, df_pool)
      lu_rice_cal = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
      lu_rice_pro = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
      lu_rice_cost = (lu.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]

      lu_total_cal = lu_main["calories"] + lu_side["calories"] + lu_rice_cal
      lu_total_pro = lu_main["protein"] + lu_side["protein"] + lu_rice_pro
      lu_total_cost = lu_main["price"] + lu_side["price"] + lu_rice_cost

      # 3. Bữa tối
      dn = meal_plan.meals.dinner
      dn_main = get_dish_info(dn.main_dish, df_pool)
      dn_side = get_dish_info(dn.side_dish, df_pool)
      dn_rice_cal = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
      dn_rice_pro = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
      dn_rice_cost = (dn.rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]

      dn_total_cal = dn_main["calories"] + dn_side["calories"] + dn_rice_cal
      dn_total_pro = dn_main["protein"] + dn_side["protein"] + dn_rice_pro
      dn_total_cost = dn_main["price"] + dn_side["price"] + dn_rice_cost

      # Tổng kết
      total_cal = bf_info["calories"] + lu_total_cal + dn_total_cal
      total_pro = bf_info["protein"] + lu_total_pro + dn_total_pro
      total_cost = bf_info["price"] + lu_total_cost + dn_total_cost

      target_cal = get_user_value(user_information, "calories_need")
      target_pro = get_user_value(user_information, "protein_need")
      budget = get_user_value(user_information, "daily_budget")

      budget_tolerance = budget * 1.05  # cho phép lố tối đa 5%
      if total_cost > budget_tolerance:
            raise InvalidResponseError(f"Thực đơn vượt quá ngân sách: {total_cost:,.0f}đ > {budget:,.0f}đ")

      return (
            f"Bữa sáng: {bf_name} ({bf_info['calories']} kcal / {bf_info['protein']}g protein / {bf_info['price']:,.0f}đ)\n"
            f"Nguyên liệu: {bf_info['ingredients']}\n\n"
            f"Bữa trưa: {lu.main_dish} + {lu.side_dish} + {lu.rice_grams}g cơm ({lu_total_cal:.0f} kcal / {lu_total_pro:.1f}g protein / {lu_total_cost:,.0f}đ)\n"
            f"Nguyên liệu: {lu_main['ingredients']}, {lu_side['ingredients']}\n\n"
            f"Bữa tối: {dn.main_dish} + {dn.side_dish} + {dn.rice_grams}g cơm ({dn_total_cal:.0f} kcal / {dn_total_pro:.1f}g protein / {dn_total_cost:,.0f}đ)\n"
            f"Nguyên liệu: {dn_main['ingredients']}, {dn_side['ingredients']}\n\n"
            f"Tổng kết ngày:\n"
            f"    Tổng Calo: {total_cal:.0f} / {target_cal} kcal\n"
            f"    Tổng Protein: {total_pro:.1f} / {target_pro} g\n"
            f"    Tổng Chi phí: {total_cost:,.0f} / {budget:,.0f} đ"
      )
#####

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

      response = await generate_chat(prompt)
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