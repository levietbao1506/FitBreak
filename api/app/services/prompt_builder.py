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
                  f"- {row['name']} | Bữa: {row['meal_type']} | Calo gốc: {row['calories']} kcal | "
                  f"Protein gốc: {row['protein_g']}g | Giá gốc: {int(row['cost_vnd']):,}đ"
            )
      food_context = "\n".join(food_items_list)

      allergen_display = allergen if allergen else "Không có"

      # Phân bổ ước tính ngân sách cho từng bữa
      est_breakfast_max = int(daily_budget * 0.28)
      est_meal_max = int(daily_budget * 0.38)

      prompt = f"""[PERSONA]
Bạn là một Chuyên Gia Dinh Dưỡng Thể Hình (Sports Nutritionist) & Chuyên Viên Thiết Kế Bữa Ăn Cá Nhân Hóa hàng đầu. Bạn có tư duy tính toán vi chất và năng lượng cực kỳ chuẩn xác, am hiểu sâu sắc về phân bổ Macro (Protein/Carb/Fat), TDEE và ẩm thực Việt Nam.

[CONTEXT]
Người dùng đang tham gia chương trình chăm sóc sức khỏe FitBreak. Họ cần một thực đơn 3 bữa đầy đủ dinh dưỡng trong ngày, được đo lường chính xác để đạt mục tiêu vóc dáng nhưng phải tuân thủ nghiêm ngặt ngân sách sinh hoạt.
Hồ sơ dinh dưỡng mục tiêu của người dùng:
- Mức năng lượng mục tiêu (TDEE): {calories_need} kcal/ngày
- Lượng Protein tối thiểu cần nạp: {protein_need} g/ngày
- Tổng ngân sách chi tiêu tối đa: {daily_budget:,} VNĐ/ngày
- Mục tiêu thể hình: {aim}
- Chế độ ăn uống: {diet_type}
- Dị ứng / Thực phẩm kiêng cữ: {allergen_display}

[DATABASE CONTEXT - DANH SÁCH MÓN ĂN HỢP LỆ ĐÃ LỌC TỪ CƠ SỞ DỮ LIỆU]
{food_context}

[QUY ƯỚC DINH DƯỠNG CƠM TRẮNG (TÍNH TRÊN 100G)]
- Năng lượng: 130 kcal | Protein: 2.7g | Giá: 2,000 VNĐ

[MISSION & INSTRUCTIONS]
Nhiệm vụ của bạn là lập kế hoạch thực đơn gồm 3 bữa (Bữa sáng, Bữa trưa, Bữa tối) đáp ứng hoàn hảo cả 3 tiêu chí:
1. ĐỦ NĂNG LƯỢNG & MACRO:
   - Tổng calo 3 bữa + cơm trắng phải tiệm cận sát mức TDEE {calories_need} kcal (sai số cho phép chỉ trong khoảng +- 5% đến 8%). KHÔNG ĐƯỢC ĐỂ THIẾU CALO.
   - Tổng Protein 3 bữa phải đạt hoặc vượt mức tối thiểu {protein_need} g.
2. CƠ CHẾ ĐIỀU CHỈNH HỆ SỐ KHẨU PHẦN (PORTION MULTIPLIER `portion_multiplier`):
   - Mỗi món ăn trong database có khẩu phần chuẩn (1.0x).
   - ĐỂ ĐẢM BẢO ĐỦ CALO VÀ PROTEIN: Bạn ĐƯỢC PHÉP và NÊN ĐIỀU CHỈNH hệ số khẩu phần `portion_multiplier` cho từng món (Ví dụ: 1.0x, 1.2x, 1.3x, 1.5x, tối đa 2.5x). Khi nhân hệ số, toàn bộ calo, protein và chi phí của món đó sẽ nhân tương ứng (Ví dụ: Phở bò 450 kcal x 1.3 = 585 kcal).
   - Kết hợp điều chỉnh lượng cơm (`rice_grams`, từ 0g đến 300g) ở bữa trưa và tối để bù đắp năng lượng sạch (Carb) tinh tế, vừa vặn TDEE.
3. TUÂN THỦ NGÂN SÁCH NGHIÊM NGẶT:
   - Tổng chi phí thực tế (Chi phí món sáng + Chi phí món trưa + Chi phí món tối [đã nhân hệ số portion_multiplier] + Tiền cơm) PHẢI <= {daily_budget:,} VNĐ. Tuyệt đối không được vượt quá dù chỉ 1 đồng.
   - Gợi ý phân bổ: Sáng ~{est_breakfast_max:,}đ, Trưa ~{est_meal_max:,}đ, Tối ~{est_meal_max:,}đ.

[CONSTRAINTS & RULES BẮT BUỘC]
- TÊN MÓN ĂN (`dish_name`, `main_dish`): BẮT BUỘC phải copy CHÍNH XÁC 100% từng ký tự từ [DANH SÁCH MÓN ĂN HỢP LỆ TRONG DATABASE]. Tuyệt đối KHÔNG tự sáng tác hay thêm bớt chữ vào tên món.
- Hệ số khẩu phần `portion_multiplier`: Là số thập phân hoặc nguyên từ 0.5 đến 2.5 (Mặc định là 1.0 nếu ăn 1 phần chuẩn).
- `rice_grams`: Số nguyên từ 0 đến 300.
- Output Format: Chỉ xuất DUY NHẤT một khối mã JSON hợp lệ theo đúng cấu trúc bên dưới, không có bất kỳ lời dẫn nhập hay bình luận giải thích nào bên ngoài.

[OUTPUT JSON SCHEMA]
```json
{{
      "estimated_total_cost": [Tổng chi phí bạn tính toán sau khi nhân hệ số và cộng tiền cơm, <= {daily_budget}],
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
