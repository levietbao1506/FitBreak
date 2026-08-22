from pathlib import Path

import pandas as pd

from api.app.core.exceptions import NoMatchingFoodsError

DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "vietnamese_food_100.csv"
df = pd.read_csv(DATA_PATH)
df["allergens"] = df["allergens"].fillna("")


def filter_foods(df, user_diet, user_allergens):
      def has_allergen(item_allergens):
            if not item_allergens:
                  return False
            item_list = [a.strip().lower() for a in item_allergens.split(";")]
            return any(a in user_allergens for a in item_list)

      if isinstance(user_allergens, str):
            user_allergens = [
                  a.strip().lower() for a in user_allergens.replace(",", ";").split(";") if a.strip()
            ]
      else:
            user_allergens = [
                  a.strip().lower() for a in (user_allergens or []) if a and a.strip()
            ]

      valid_df = df[~df["allergens"].apply(has_allergen)].copy()

      if user_diet:
            normalized_diet = str(user_diet).strip().lower()
            valid_df = valid_df[
                  valid_df["diet_type"].apply(
                        lambda diets: normalized_diet in {
                              diet.strip().lower() for diet in diets.split(";")
                        }
                  )
            ]

      return valid_df


async def prompt_builder(
    calories_need: int,
    daily_budget: int,
    protein_need: int,
    aim: str,
    diet_type: str,
    allergen: str,
) -> str:
      filtered_food = filter_foods(df, diet_type, allergen)
      if filtered_food.empty:
            raise NoMatchingFoodsError("Không tìm thấy món ăn phù hợp với chế độ ăn và dị ứng")

      food_items_list = []
      for _, row in filtered_food.iterrows():
            food_items_list.append(
                  f"- {row['name']} | Bữa: {row['meal_type']} | Calo: {row['calories']} kcal | "
                  f"Protein: {row['protein_g']}g | Giá: {int(row['cost_vnd']):,}đ"
            )
      food_context = "\n".join(food_items_list)

      prompt = f"""Bạn là một chuyên gia dinh dưỡng và lập kế hoạch bữa ăn. Hãy gợi ý thực đơn 3 bữa trong ngày dựa trên dữ liệu và thông tin người dùng dưới đây.

      === DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE ===
      {food_context}

      === THÔNG TIN NGƯỜI DÙNG ===
      - Mục tiêu calo: {calories_need} kcal
      - Mục tiêu protein: {protein_need} g
      - Ngân sách mỗi ngày: {daily_budget:,} VNĐ
      - Mục tiêu thể hình: {aim}
      - Chế độ ăn: {diet_type}

      === QUY TẮC BẮT BUỘC ===
      1. CHỈ ĐƯỢC CHỌN món có trong [DANH SÁCH MÓN ĂN HỢP LỆ]. Tuyệt đối không tự bịa tên món ăn ngoài danh sách.
      Cơm là thành phần cố định, không phải món trong database, và luôn tính theo quy ước bên dưới.
      2. Cấu trúc bữa ăn:
      - Bữa sáng: 1 món (chọn từ các món có bữa là breakfast).
      - Bữa trưa: Món chính + Món rau/canh + Cơm.
      - Bữa tối: Món chính + Món rau/canh + Cơm.
      *(Quy ước mặc định cho 1 chén Cơm: 200 kcal / 4g protein / 5.000đ)*.
      3. Tính toán tổng Calo, tổng Protein và tổng Chi phí của cả ngày:
      - Cố gắng bám sát nhất có thể với target Calo và Protein.
      - Tổng chi phí KHÔNG ĐƯỢC vượt quá ngân sách {daily_budget:,} VNĐ.

      === FORMAT BẮT BUỘC (Xuất chính xác theo mẫu, không thêm lời chào hay giải thích rườm rà) ===
      Bữa sáng: [Tên món] + ([Calo] kcal / [Protein]g / [Giá]đ)
      Bữa trưa: [Món chính] + [Món rau/canh] + Cơm + ([Tổng Calo trưa] kcal / [Tổng Protein trưa]g / [Tổng Giá trưa]đ)
      Bữa tối: [Món chính] + [Món rau/canh] + Cơm + ([Tổng Calo tối] kcal / [Tổng Protein tối]g / [Tổng Giá tối]đ)

      Tổng kết ngày:
      Tổng Calo: [Tổng cả ngày] / {calories_need} kcal
      Tổng Protein: [Tổng cả ngày] / {protein_need} g
      Tổng Chi phí: [Tổng cả ngày] / {daily_budget:,} đ"""

      return prompt