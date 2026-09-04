import pandas as pd

async def prompt_builder(
      calories_need: int,
      daily_budget: int,
      protein_need: int,
      aim: str,
      diet_type: str,
      allergen: str,
      filtered_food: pd.DataFrame,
) -> str:
      # 1. Format danh sách món ăn từ DataFrame
      food_items_list = []
      for _, row in filtered_food.iterrows():
            food_items_list.append(
                  f"- {row['name']} | Bữa: {row['meal_type']} | Calo: {row['calories']} kcal | "
                  f"Protein: {row['protein_g']}g | Giá: {int(row['cost_vnd']):,}đ"
            )
      food_context = "\n".join(food_items_list)

      allergen_display = allergen if allergen else "Không có"

      # 2. Xây dựng prompt
      # Phân bổ trần chi phí cho từng bữa để LLM dễ kiểm soát
      est_breakfast_max = int(daily_budget * 0.25)
      est_meal_max = int(daily_budget * 0.35)

      prompt = f"""Bạn là một chuyên gia dinh dưỡng và lập kế hoạch bữa ăn. Hãy gợi ý thực đơn 3 bữa trong ngày dựa trên dữ liệu và thông tin người dùng dưới đây.

=== DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE ===
{food_context}

=== THÔNG TIN NGƯỜI DÙNG ===
- Mục tiêu calo: {calories_need} kcal
- Mục tiêu protein: {protein_need} g
- Ngân sách tối đa mỗi ngày: {daily_budget:,} VNĐ
- Mục tiêu thể hình: {aim}
- Chế độ ăn: {diet_type}
- Dị ứng: {allergen_display}

=== QUY ƯỚC DINH DƯỠNG CỦA CƠM (TÍNH TRÊN 100G) ===
- Calo: 130 kcal | Protein: 2.7g | Chi phí: 2,000 VNĐ

=== NGUYÊN TẮC KIỂM SOÁT NGÂN SÁCH (BẮT BUỘC TUÂN THỦ) ===
1. TỔNG CHI PHÍ 3 BỮA + TIỀN CƠM PHẢI <= {daily_budget:,} VNĐ. Tuyệt đối không được vượt quá dù chỉ 1 đồng.
2. Hướng dẫn phân bổ chi phí để không bị lố:
   - Bữa sáng: Chọn món dưới {est_breakfast_max:,} VNĐ.
   - Bữa trưa (Món chính + Cơm): Tổng dưới {est_meal_max:,} VNĐ.
   - Bữa tối (Món chính + Cơm): Tổng dưới {est_meal_max:,} VNĐ.
   - Nếu ngân sách thấp, ưu tiên các món bình dân giá rẻ trong danh sách.

=== QUY TẮC CHỌN MÓN BẮT BUỘC ===
1. CHỈ ĐƯỢC CHỌN TÊN MÓN XUẤT HIỆN TRONG [DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE]. TUYỆT ĐỐI KHÔNG TỰ BỊA RA TÊN MÓN NÀO KHÁC. COPY CHÍNH XÁC 100% TỪNG CHỮ CỦA TÊN MÓN.
2. Cấu trúc thực đơn:
   - Bữa sáng: 1 món (phù hợp cho bữa sáng).
   - Bữa trưa: 1 món chính (main_dish) + Điều chỉnh lượng cơm (`rice_grams`) sao cho (Tổng Calo 3 bữa + Cơm) ~ {calories_need} kcal (sai số cho phép +- 10%). Tối đa 300g cơm mỗi bữa.
   - Bữa tối: 1 món chính (main_dish) + Điều chỉnh lượng cơm (`rice_grams`) sao cho (Tổng Calo 3 bữa + Cơm) ~ {calories_need} kcal (sai số cho phép +- 10%). Tối đa 300g cơm mỗi bữa.

=== FORMAT JSON BẮT BUỘC (Chỉ xuất duy nhất block JSON, không kèm lời giải thích bên ngoài) ===
```json
{{
      "estimated_total_cost": [Tổng chi phí bạn nhẩm tính của 3 bữa và cơm, phải nhỏ hơn hoặc bằng {daily_budget}],
      "meals": {{
      "breakfast": {{
            "dish_name": "Copy chính xác tên món từ danh sách"
      }},
      "lunch": {{
            "main_dish": "Copy chính xác tên món từ danh sách",
            "rice_grams": 150
      }},
      "dinner": {{
            "main_dish": "Copy chính xác tên món từ danh sách",
            "rice_grams": 150
      }}
      }}
}}
```"""

      return prompt