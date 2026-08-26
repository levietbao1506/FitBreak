import json
import re
from pydantic import BaseModel, Field
from typing import List

from api.app.core.exceptions import (
      InvalidResponseError,
      InvalidUserInformationError
)
from api.app.core.ollama_client import generate_chat
from api.app.services.prompt_builder import df, prompt_builder

class Breakfast(BaseModel):
    dish_name: str

class MainMeal(BaseModel):
    main_dish: str
    side_dish: str
    rice_grams: int = Field(default=0, description="Số gram cơm")

class MealsPlan(BaseModel):
    breakfast: Breakfast
    lunch: MainMeal
    dinner: MainMeal

class LLMMealResponse(BaseModel):
    meals: MealsPlan

# 2. Hàm trích xuất an toàn từ response raw của LLM
def parse_llm_meal_response(raw_text: str) -> LLMMealResponse:
      # Lấy chuỗi JSON từ chuỗi kết quả (bỏ qua lời chào nếu LLM lỡ sinh ra)
      match = re.search(r'\{.*\}', raw_text, re.DOTALL)
      if not match:
            raise ValueError("LLM không trả về JSON hợp lệ")
      
      clean_json = match.group(0)
      data = json.loads(clean_json)

      return LLMMealResponse(**data)

def get_user_value(user_information: dict, field: str, default=None):
      if isinstance(user_information, dict):
            return user_information.get(field, default)
      return getattr(user_information, field, default)


def validate_user_information(user_information: dict) -> None:
      required_fields = ("calories_need", "daily_budget", "protein_need", "aim", "diet_type")
      missing_fields = [
            field for field in required_fields
            if get_user_value(user_information, field) is None
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

'''
Format:
Bữa sáng: Tên món + (Calo / Protein / Giá)
Bữa trưa: Món chính + Món rau/canh + Cơm + (Calo / Protein / Giá)
Bữa tối: Món chính + Món rau/canh + Cơm + (Calo / Protein / Giá)
Tổng kết ngày:
      Tổng Calo: ... / Target kcal
      Tổng Protein: ... / Target g
      Tổng Chi phí: ... / Budget đ
'''

import pandas as pd

def get_dish_stats(name: str):
      matches = df[df['name'].str.lower() == name.lower().strip()]
      if matches.empty:
            raise InvalidResponseError(f"Món ăn không có trong database: {name}")
      row = matches.iloc[0]
      return {
            "name": str(row["name"]),
            "calories": int(row["calories"]),
            "protein_g": float(row["protein_g"]),
            "cost_vnd": int(row["cost_vnd"]),
            "ingredients": str(row["ingredients"]) if pd.notna(row["ingredients"]) else str(row["name"])
      }

def validate_generated_response(response: str, user_info: dict) -> str:
      try:
            meal_plan = parse_llm_meal_response(response)
      except Exception:
            raise InvalidResponseError("Response không đúng định dạng JSON")

      daily_budget = get_user_value(user_info, "daily_budget")
      target_calo = get_user_value(user_info, "calories_need")
      target_protein = get_user_value(user_info, "protein_need")
      
      try:
            bf = get_dish_stats(meal_plan.meals.breakfast.dish_name)
            l_main = get_dish_stats(meal_plan.meals.lunch.main_dish)
            l_side = get_dish_stats(meal_plan.meals.lunch.side_dish)
            d_main = get_dish_stats(meal_plan.meals.dinner.main_dish)
            d_side = get_dish_stats(meal_plan.meals.dinner.side_dish)
      except InvalidResponseError as e:
            raise e

      def calc_rice(grams: int):
            ratio = grams / 200.0 if grams else 1.0
            return {
                  "calories": int(200 * ratio),
                  "protein_g": float(4 * ratio),
                  "cost_vnd": int(5000 * ratio)
            }

      l_rice = calc_rice(meal_plan.meals.lunch.rice_grams)
      d_rice = calc_rice(meal_plan.meals.dinner.rice_grams)

      total_calo = bf["calories"] + l_main["calories"] + l_side["calories"] + l_rice["calories"] + d_main["calories"] + d_side["calories"] + d_rice["calories"]
      total_protein = bf["protein_g"] + l_main["protein_g"] + l_side["protein_g"] + l_rice["protein_g"] + d_main["protein_g"] + d_side["protein_g"] + d_rice["protein_g"]
      total_cost = bf["cost_vnd"] + l_main["cost_vnd"] + l_side["cost_vnd"] + l_rice["cost_vnd"] + d_main["cost_vnd"] + d_side["cost_vnd"] + d_rice["cost_vnd"]

      if total_cost > daily_budget:
            raise InvalidResponseError("Thực đơn vượt quá ngân sách")

      res = []
      res.append(f"Bữa sáng: {bf['name']} + ({bf['calories']} kcal / {bf['protein_g']}g / {bf['cost_vnd']:,}đ)")
      res.append(f"Nguyên liệu: {bf['ingredients']}\n")

      l_calo = l_main["calories"] + l_side["calories"] + l_rice["calories"]
      l_pro = l_main["protein_g"] + l_side["protein_g"] + l_rice["protein_g"]
      l_cost = l_main["cost_vnd"] + l_side["cost_vnd"] + l_rice["cost_vnd"]
      res.append(f"Bữa trưa: {l_main['name']} + {l_side['name']} + Cơm + ({l_calo} kcal / {l_pro}g / {l_cost:,}đ)")
      res.append(f"Nguyên liệu: {l_main['ingredients']}, {l_side['ingredients']}\n")

      d_calo = d_main["calories"] + d_side["calories"] + d_rice["calories"]
      d_pro = d_main["protein_g"] + d_side["protein_g"] + d_rice["protein_g"]
      d_cost = d_main["cost_vnd"] + d_side["cost_vnd"] + d_rice["cost_vnd"]
      res.append(f"Bữa tối: {d_main['name']} + {d_side['name']} + Cơm + ({d_calo} kcal / {d_pro}g / {d_cost:,}đ)")
      res.append(f"Nguyên liệu: {d_main['ingredients']}, {d_side['ingredients']}\n")

      res.append("Tổng kết ngày:")
      res.append(f"      Tổng Calo: {total_calo} / {target_calo} kcal")
      res.append(f"      Tổng Protein: {total_protein} / {target_protein} g")
      res.append(f"      Tổng Chi phí: {total_cost:,} / {daily_budget:,} đ")

      return "\n".join(res)

async def process_rag_pipeline(
      user_information: dict
) -> str:
      validate_user_information(user_information)
      prompt = await prompt_builder(
            get_user_value(user_information, "calories_need"),
            get_user_value(user_information, "daily_budget"),
            get_user_value(user_information, "protein_need"),
            get_user_value(user_information, "aim"),
            get_user_value(user_information, "diet_type"),
            get_user_value(user_information, "allergen", "")
      )
      response = await generate_chat(prompt)
      return validate_generated_response(response, user_information)
