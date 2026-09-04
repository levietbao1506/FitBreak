from typing import List, Optional
import pandas as pd


async def prompt_builder(
    calories_need: int,
    daily_budget: int,
    protein_need: int,
    aim: str,
    diet_type: str,
    allergen: str,
    filtered_food: pd.DataFrame,
    exclude_dishes: Optional[List[str]] = None,
) -> str:
    # 1. Loại bỏ các món đã ăn trước đó nếu còn đủ lựa chọn
    candidates_df = filtered_food.copy()
    if exclude_dishes:
        clean_exclude = {d.strip().lower() for d in exclude_dishes if d and d.strip()}
        remaining = candidates_df[~candidates_df["name"].str.strip().str.lower().isin(clean_exclude)]
        # Chỉ loại bỏ nếu còn ít nhất 6 món để chọn
        if len(remaining) >= 6:
            candidates_df = remaining

    # 2. Phân chia ứng viên cho bữa sáng và bữa chính (trưa/tối)
    bf_candidates = candidates_df[candidates_df["meal_type"].str.contains("breakfast", case=False, na=False)]
    main_candidates = candidates_df[candidates_df["meal_type"].str.contains("lunch|dinner", case=False, na=False)]

    # Xáo trộn và lấy mẫu đa dạng
    shuffled_bf = bf_candidates.sample(frac=1).head(6) if not bf_candidates.empty else candidates_df.head(4)
    shuffled_main = main_candidates.sample(frac=1).head(10) if not main_candidates.empty else candidates_df.tail(8)

    bf_items = []
    for _, row in shuffled_bf.iterrows():
        bf_items.append(
            f"- {row['name']} | Calo: {row['calories']} kcal | Protein: {row['protein_g']}g | Giá: {int(row['cost_vnd']):,}đ"
        )
    bf_context = "\n".join(bf_items)

    main_items = []
    for _, row in shuffled_main.iterrows():
        main_items.append(
            f"- {row['name']} | Calo: {row['calories']} kcal | Protein: {row['protein_g']}g | Giá: {int(row['cost_vnd']):,}đ"
        )
    main_context = "\n".join(main_items)

    allergen_display = allergen if allergen else "Không có"
    exclude_text = ""
    if exclude_dishes:
        valid_exclude = [d for d in exclude_dishes if d and d.strip()]
        if valid_exclude:
            exclude_text = f"\n=== YÊU CẦU ĐỔI MỚI THỰC ĐƠN ===\n- TUYỆT ĐỐI KHÔNG CHỌN LẠI các món sau đây: {', '.join(valid_exclude)}. Hãy chọn các món hoàn toàn khác.\n"

    est_breakfast_max = int(daily_budget * 0.25)
    est_meal_max = int(daily_budget * 0.35)

    prompt = f"""Bạn là chuyên gia dinh dưỡng lập kế hoạch bữa ăn. Hãy chọn thực đơn 3 bữa trong ngày từ danh sách dưới đây.

=== DANH SÁCH MÓN CHO BỮA SÁNG (Chỉ chọn 1 món từ đây cho breakfast) ===
{bf_context}

=== DANH SÁCH MÓN CHO BỮA TRƯA & TỐI (Chỉ chọn 2 món khác nhau từ đây cho lunch và dinner) ===
{main_context}
{exclude_text}
=== THÔNG TIN NGƯỜI DÙNG ===
- Mục tiêu calo: {calories_need} kcal
- Mục tiêu protein: {protein_need} g
- Ngân sách tối đa: {daily_budget:,} VNĐ
- Chế độ: {diet_type} | Thể hình: {aim} | Dị ứng: {allergen_display}

=== QUY ƯỚC DINH DƯỠNG CỦA CƠM (100G) ===
- Calo: 130 kcal | Protein: 2.7g | Giá: 2,000 VNĐ

=== QUY TẮC BẮT BUỘC (TUÂN THỦ 100%) ===
1. 3 BỮA SÁNG, TRƯA, TỐI PHẢI LÀ 3 MÓN HOÀN TOÀN KHÁC NHAU. TUYỆT ĐỐI KHÔNG TRÙNG MÓN.
2. Bữa sáng: Chọn 1 món từ [DANH SÁCH MÓN CHO BỮA SÁNG].
3. Bữa trưa và Bữa tối: Chọn 2 món khác nhau từ [DANH SÁCH MÓN CHO BỮA TRƯA & TỐI].
4. Quy tắc cơm trắng (`rice_grams`):
   - Món có sẵn tinh bột (Bún, Phở, Mì, Bánh mì, Cơm tấm, Hủ tiếu, Miến, Cháo): BẮT BUỘC đặt `rice_grams` = 0.
   - Món mặn ăn với cơm (Thịt/cá kho, xào, luộc, canh): Đặt `rice_grams` từ 100 đến 200g.
5. Tổng chi phí 3 bữa + tiền cơm <= {daily_budget:,} VNĐ.

=== FORMAT JSON BẮT BUỘC (Chỉ xuất duy nhất block JSON) ===
```json
{{
  "estimated_total_cost": {daily_budget},
  "meals": {{
    "breakfast": {{
      "dish_name": "Tên món chính xác từ danh sách bữa sáng"
    }},
    "lunch": {{
      "main_dish": "Tên món chính xác từ danh sách trưa/tối",
      "rice_grams": 0
    }},
    "dinner": {{
      "main_dish": "Tên món chính xác khác từ danh sách trưa/tối",
      "rice_grams": 150
    }}
  }}
}}
```"""

    return prompt