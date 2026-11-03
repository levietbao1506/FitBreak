import pandas as pd

async def prompt_builder(
      calories_need: int,
      daily_budget: int,
      protein_need: int,
      aim: str,
      diet_type: str,
      allergen: str,
      filtered_food: pd.DataFrame,
      food_recommendation: str = None,
) -> str:
      # 1. Format danh sách món ăn từ DataFrame
      food_items_list = []
      for _, row in filtered_food.iterrows():
            food_items_list.append(
                  f"- {row['name']} | Bữa: {row['meal_type']} | Calo gốc: {row['calories']} kcal | "
                  f"Protein gốc: {row['protein_g']}g | Giá gốc: {int(row['cost_vnd']):,}đ"
            )
      food_context = "\n".join(food_items_list)

      allergen_display = allergen if allergen else "Không có"

      # Phần lưu ý y tế đặc biệt nếu có
      medical_section = ""
      if food_recommendation and food_recommendation.strip():
            medical_section = f"""
=== LỜI KHUYÊN & LƯU Ý DINH DƯỠNG Y TẾ (TỪ HỒ SƠ SỨC KHỎE / MEDICAL CHECKUP) ===
Chú ý y tế quan trọng của người dùng:
"{food_recommendation.strip()}"
-> BẮT BUỘC: Bạn PHẢI ưu tiên chọn các món ăn phù hợp với lưu ý y tế trên (Ví dụ: nếu tiểu đường / tiền tiểu đường thì tránh món nhiều đường, ưu tiên chất xơ; nếu huyết áp cao thì hạn chế món mặn; nếu thừa cân thì thâm hụt calo lành mạnh).
"""

      # 2. Phân bổ ước tính ngân sách & năng lượng mục tiêu cho từng bữa
      b_budget_target = int(daily_budget * 0.25)
      b_budget_max = int(daily_budget * 0.28)
      b_cal_target = int(calories_need * 0.25)

      l_budget_target = int(daily_budget * 0.38)
      l_budget_max = int(daily_budget * 0.40)
      l_cal_target = int(calories_need * 0.40)

      d_budget_target = int(daily_budget * 0.34)
      d_budget_max = int(daily_budget * 0.35)
      d_cal_target = int(calories_need * 0.35)

      prompt = f"""[PERSONA]
Bạn là một Chuyên Gia Dinh Dưỡng Thể Hình (Sports Nutritionist) & Bác Sĩ Dinh Dưỡng Lâm Sàng hàng đầu. Bạn có khả năng tính toán vi chất và năng lượng cực kỳ chuẩn xác, thấu hiểu tình trạng bệnh lý/sức khỏe và ẩm thực Việt Nam để đưa ra thực đơn an toàn, tối ưu nhất.

[CONTEXT]
Người dùng đang tham gia chương trình chăm sóc sức khỏe FitBreak. Họ cần một thực đơn 3 bữa đầy đủ dinh dưỡng trong ngày, được đo lường chính xác để đạt mục tiêu vóc dáng, phù hợp với tình trạng sức khỏe cá nhân nhưng phải tuân thủ nghiêm ngặt ngân sách sinh hoạt.

Hồ sơ dinh dưỡng & sức khỏe của người dùng:
- Mức năng lượng mục tiêu (TDEE): {calories_need} kcal/ngày
- Lượng Protein tối thiểu cần nạp: {protein_need} g/ngày
- Tổng ngân sách chi tiêu tối đa: {daily_budget:,} VNĐ/ngày
- Mục tiêu thể hình: {aim}
- Chế độ ăn uống: {diet_type}
- Dị ứng / Thực phẩm kiêng cữ: {allergen_display}
{medical_section}
[DATABASE CONTEXT - DANH SÁCH MÓN ĂN HỢP LỆ ĐÃ LỌC TỪ CƠ SỞ DỮ LIỆU]
{food_context}

[QUY ƯỚC DINH DƯỠNG CƠM TRẮNG (TÍNH TRÊN 100G)]
- Năng lượng: 130 kcal | Protein: 2.7g | Giá: 2,000 VNĐ

[BẢNG PHÂN BỔ ƯỚC TÍNH NGÂN SÁCH & NĂNG LƯỢNG CHO TỪNG BỮA]
1. BỮA SÁNG (~25% - 28% ngân sách):
   - Ngân sách ước tính: Khoảng {b_budget_target:,} VNĐ (Tối đa không vượt quá {b_budget_max:,} VNĐ).
   - Năng lượng mục tiêu: Khoảng ~{b_cal_target} kcal.
2. BỮA TRƯA (~38% - 40% ngân sách):
   - Ngân sách ước tính: Khoảng {l_budget_target:,} VNĐ (Tối đa không vượt quá {l_budget_max:,} VNĐ bao gồm cả món chính và cơm).
   - Năng lượng mục tiêu: Khoảng ~{l_cal_target} kcal.
3. BỮA TỐI (~34% - 35% ngân sách):
   - Ngân sách ước tính: Khoảng {d_budget_target:,} VNĐ (Tối đa không vượt quá {d_budget_max:,} VNĐ bao gồm cả món chính và cơm).
   - Năng lượng mục tiêu: Khoảng ~{d_cal_target} kcal.

[MISSION & INSTRUCTIONS]
Lập kế hoạch thực đơn gồm 3 bữa đáp ứng hoàn hảo các tiêu chí:
1. ĐỦ NĂNG LƯỢNG & MACRO:
   - Tổng calo 3 bữa + cơm trắng tiệm cận sát TDEE {calories_need} kcal (sai số +- 5% đến 8%). KHÔNG ĐƯỢC THIẾU CALO.
   - Tổng Protein đạt hoặc vượt mức tối thiểu {protein_need} g.
2. ĐA DẠNG MÓN ĂN (BẮT BUỘC KHÔNG TRÙNG LẶP):
   - 3 món ăn cho 3 bữa (Sáng, Trưa, Tối) **BẮT BUỘC PHẢI KHÁC NHAU HOÀN TOÀN**, tuyệt đối không lặp lại cùng một món trong ngày.
3. CƠ CHẾ ĐIỀU CHỈNH HỆ SỐ KHẨU PHẦN (`portion_multiplier`):
   - `portion_multiplier`: Số thập phân hoặc nguyên từ 0.5 đến 2.5 (Mặc định 1.0).
   - `rice_grams`: Số nguyên từ 0 đến 300 (cho bữa trưa và tối) để bổ sung năng lượng sạch vừa vặn TDEE.
4. TUÂN THỦ NGÂN SÁCH (HỆ THỐNG BACKEND SẼ TỰ ĐỘNG TÍNH TOÁN LẠI CHI PHÍ CHÍNH XÁC):
   - Tổng chi phí thực tế (Chi phí 3 món [sau nhân hệ số] + Tiền cơm) PHẢI <= {daily_budget:,} VNĐ.
   - Bạn có thể ghi nhẩm tính hoặc để giá trị 0 ở trường `estimated_total_cost`, backend sẽ tự động tính toán tổng số tiền thực tế chuẩn xác 100%.
5. LỜI KHUYÊN Y TẾ & GIẢI THÍCH:
   - Giải thích rõ tại `nutrition_note` lý do chọn món, cách cân bằng calo và cách hỗ trợ kiểm soát chỉ số sức khỏe của người dùng.

[CONSTRAINTS & RULES BẮT BUỘC]
- TÊN MÓN ĂN (`dish_name`): BẮT BUỘC dùng chung khóa `dish_name` cho cả 3 bữa. Copy CHÍNH XÁC 100% từng ký tự từ [DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE]. Không tự sáng tác hay thêm bớt chữ.
- Output Format: Chỉ xuất DUY NHẤT một khối mã JSON hợp lệ theo đúng cấu trúc bên dưới, không kèm text hay lời dẫn ngoài.

[OUTPUT JSON SCHEMA]
```json
{{
      "estimated_total_cost": 0,
      "nutrition_note": "Lời giải thích ngắn gọn: vì sao thực đơn này đáp ứng TDEE/Protein, cách phân bổ ngân sách 3 bữa và phù hợp với tình trạng sức khỏe / lời khuyên y tế của bạn",
      "meals": {{
            "breakfast": {{
                  "dish_name": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.0
            }},
            "lunch": {{
                  "dish_name": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.2,
                  "rice_grams": 150
            }},
            "dinner": {{
                  "dish_name": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.0,
                  "rice_grams": 150
            }}
      }}
}}
```"""

      return prompt
