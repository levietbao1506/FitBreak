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
⚠️ Chú ý y tế quan trọng của người dùng:
"{food_recommendation.strip()}"
-> BẮT BUỘC: Bạn PHẢI ưu tiên chọn các món ăn phù hợp với lưu ý y tế trên (Ví dụ: nếu tiểu đường / tiền tiểu đường thì tránh món nhiều đường, ưu tiên chất xơ; nếu huyết áp cao thì hạn chế món mặn; nếu thừa cân thì thâm hụt calo lành mạnh).
"""

      # Phân bổ ước tính ngân sách cho từng bữa
      est_breakfast_max = int(daily_budget * 0.28)
      est_meal_max = int(daily_budget * 0.38)

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

[MISSION & INSTRUCTIONS]
Nhiệm vụ của bạn là lập kế hoạch thực đơn gồm 3 bữa (Bữa sáng, Bữa trưa, Bữa tối) đáp ứng hoàn hảo các tiêu chí:
1. ĐỦ NĂNG LƯỢNG & MACRO:
   - Tổng calo 3 bữa + cơm trắng phải tiệm cận sát mức TDEE {calories_need} kcal (sai số cho phép trong khoảng +- 5% đến 8%). KHÔNG ĐƯỢC ĐỂ THIẾU CALO.
   - Tổng Protein 3 bữa phải đạt hoặc vượt mức tối thiểu {protein_need} g.
2. CƠ CHẾ ĐIỀU CHỈNH HỆ SỐ KHẨU PHẦN (`portion_multiplier`):
   - Bạn ĐƯỢC PHÉP và NÊN ĐIỀU CHỈNH hệ số khẩu phần `portion_multiplier` cho từng món (Ví dụ: 1.0, 1.2, 1.3, 1.5, tối đa 2.5). Khi nhân hệ số, toàn bộ calo, protein và chi phí của món đó sẽ nhân tương ứng.
   - Kết hợp điều chỉnh lượng cơm (`rice_grams`, từ 0g đến 300g) ở bữa trưa và tối để bổ sung năng lượng sạch (Carb) vừa vặn TDEE.
3. TUÂN THỦ LỜI KHUYÊN Y TẾ:
   - Nếu có lời khuyên y tế, hãy giải thích rõ trong trường `nutrition_note` lý do tại sao bạn lựa chọn các món ăn này và cách thực đơn hỗ trợ kiểm soát chỉ số sức khỏe của người dùng.
4. TUÂN THỦ NGÂN SÁCH NGHIÊM NGẶT:
   - Tổng chi phí thực tế (Chi phí 3 món [sau nhân hệ số] + Tiền cơm) PHẢI <= {daily_budget:,} VNĐ. Tuyệt đối không được vượt quá dù chỉ 1 đồng.
   - Gợi ý phân bổ: Sáng ~{est_breakfast_max:,}đ, Trưa ~{est_meal_max:,}đ, Tối ~{est_meal_max:,}đ.

[CONSTRAINTS & RULES BẮT BUỘC]
- TÊN MÓN ĂN (`dish_name`, `main_dish`): BẮT BUỘC phải copy CHÍNH XÁC 100% từng ký tự từ [DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE]. Tuyệt đối KHÔNG tự sáng tác hay thêm bớt chữ vào tên món.
- `nutrition_note`: Một đoạn giải thích ngắn gọn, súc tích (khoảng 2-3 câu) giải thích vì sao thực đơn này được chọn, cách cân đối Calo/Protein và sự tương thích với tình trạng sức khỏe / lời khuyên y tế của người dùng.
- Hệ số khẩu phần `portion_multiplier`: Số thập phân hoặc nguyên từ 0.5 đến 2.5 (Mặc định 1.0).
- `rice_grams`: Số nguyên từ 0 đến 300.
- Output Format: Chỉ xuất DUY NHẤT một khối mã JSON hợp lệ theo đúng cấu trúc bên dưới, không có bất kỳ lời dẫn nhập hay bình luận giải thích nào bên ngoài.

[OUTPUT JSON SCHEMA]
```json
{{
      "estimated_total_cost": [Tổng chi phí bạn tính toán sau khi nhân hệ số và cộng tiền cơm, <= {daily_budget}],
      "nutrition_note": "Lời giải thích ngắn gọn: vì sao thực đơn này đáp ứng TDEE/Protein và phù hợp với tình trạng sức khỏe / lời khuyên y tế của bạn",
      "meals": {{
            "breakfast": {{
                  "dish_name": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.0
            }},
            "lunch": {{
                  "main_dish": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.2,
                  "rice_grams": 150
            }},
            "dinner": {{
                  "main_dish": "Tên món copy chính xác từ danh sách",
                  "portion_multiplier": 1.0,
                  "rice_grams": 150
            }}
      }}
}}
```"""

      return prompt
