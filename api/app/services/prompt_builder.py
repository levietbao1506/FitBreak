import random
from typing import Optional
import pandas as pd


async def prompt_builder(
    calories_need: int,
    daily_budget: int,
    protein_need: int,
    aim: str,
    diet_type: str,
    allergen: str,
    filtered_food: pd.DataFrame,
    exclude_dishes: Optional[list[str]] = None,
) -> str:
    # 1. Loại trừ các món vừa gợi ý nếu có (để khi bấm Đổi thực đơn sẽ ra món mới)
    available_df = filtered_food.copy()
    if exclude_dishes:
        exclude_lower = [d.strip().lower() for d in exclude_dishes if d]
        available_df = available_df[~available_df["name"].str.strip().str.lower().isin(exclude_lower)]
        # Nếu loại trừ xong bị quá ít món, fallback lại danh sách ban đầu
        if len(available_df) < 5:
            available_df = filtered_food.copy()

    # 2. Phân chia nhóm món sáng & trưa/tối và lấy mẫu ngẫu nhiên để tối ưu tốc độ CPU Ollama
    breakfast_df = available_df[
        available_df["meal_type"].str.contains("breakfast", case=False, na=False)
    ]
    main_df = available_df[
        available_df["meal_type"].str.contains("lunch|dinner", case=False, na=False)
    ]

    # Nếu nhóm nào rỗng thì lấy từ available_df
    if breakfast_df.empty:
        breakfast_df = available_df
    if main_df.empty:
        main_df = available_df

    # Lấy mẫu tối đa 6 món sáng và 10 món trưa/tối
    sample_breakfast = breakfast_df.sample(n=min(6, len(breakfast_df)))
    sample_main = main_df.sample(n=min(10, len(main_df)))

    # Format danh sách món cho LLM
    breakfast_list = [
        f"- {r['name']} | Calo: {r['calories']} kcal | Protein: {r['protein_g']}g | Giá: {int(r['cost_vnd']):,}đ"
        for _, r in sample_breakfast.iterrows()
    ]
    main_list = [
        f"- {r['name']} | Calo: {r['calories']} kcal | Protein: {r['protein_g']}g | Giá: {int(r['cost_vnd']):,}đ"
        for _, r in sample_main.iterrows()
    ]

    allergen_display = allergen if allergen else "Không có"

    # Phân bổ trần chi phí cho từng bữa để LLM dễ kiểm soát
    est_breakfast_max = int(daily_budget * 0.3)
    est_meal_max = int(daily_budget * 0.4)

    prompt = f"""Bạn là một chuyên gia dinh dưỡng và lập kế hoạch bữa ăn người Việt. Hãy gợi ý thực đơn 3 bữa (Sáng, Trưa, Tối) phong phú, ngon miệng và cân đối dinh dưỡng.

=== DANH SÁCH MÓN ĂN GỢI Ý HỢP LỆ (DATABASE) ===
[MÓN BỮA SÁNG]:
{chr(10).join(breakfast_list)}

[MÓN BỮA TRƯA & TỐI]:
{chr(10).join(main_list)}

=== THÔNG TIN NGƯỜI DÙNG ===
- Mục tiêu calo cả ngày: ~{calories_need} kcal
- Mục tiêu protein: ~{protein_need} g
- Ngân sách tối đa mỗi ngày: {daily_budget:,} VNĐ
- Mục tiêu thể hình: {aim}
- Chế độ ăn: {diet_type}
- Dị ứng: {allergen_display}

=== QUY ƯỚC DINH DƯỠNG CỦA CƠM TRẮNG (TÍNH TRÊN 100G) ===
- Calo: 130 kcal | Protein: 2.7g | Chi phí: 2,000 VNĐ

=== NGUYÊN TẮC BẮT BUỘC ===
1. TỔNG CHI PHÍ 3 BỮA + TIỀN CƠM PHẢI <= {daily_budget:,} VNĐ.
2. PHÂN BỔ THAM KHẢO: Sáng <= {est_breakfast_max:,}đ, Trưa <= {est_meal_max:,}đ, Tối <= {est_meal_max:,}đ.
3. CHỌN TÊN MÓN: CHỈ ĐƯỢC CHỌN TÊN TỪ DANH SÁCH TRÊN. COPY CHÍNH XÁC 100% TỪNG CHỮ CỦA TÊN MÓN.
4. KHÔNG TRÙNG LẶP: 3 bữa Sáng, Trưa, Tối TUYỆT ĐỐI KHÔNG ĐƯỢC TRÙNG NHAU (phải chọn 3 món khác nhau).
5. QUY TẮC CƠM (`rice_grams`):
   - Với món đã có sợi/tinh bột (Phở, Bún, Hủ tiếu, Bánh mì, Cơm tấm, Miến, Cháo, Xôi): ĐẶT `rice_grams: 0`.
   - Với các món xào, kho, canh, áp chảo: Đặt `rice_grams` từ 100 đến 250 để đạt mục tiêu calo.

=== FORMAT JSON BẮT BUỘC (Chỉ xuất duy nhất JSON hợp lệ, không giải thích) ===
```json
{{
  "estimated_total_cost": {daily_budget},
  "meals": {{
    "breakfast": {{
      "dish_name": "Tên món từ danh sách món sáng"
    }},
    "lunch": {{
      "main_dish": "Tên món trưa từ danh sách món trưa/tối",
      "rice_grams": 150
    }},
    "dinner": {{
      "main_dish": "Tên món tối từ danh sách món trưa/tối (khác món trưa)",
      "rice_grams": 150
    }}
  }}
}}
```"""

    return prompt