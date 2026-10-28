'''
BMI:
- 0: Nhẹ cân
- 1: Bình thường
- 2: Tiền béo phì
- 3: Béo phì độ I
- 4: Béo phì độ II
'''
def classify_BMI(
      weight: float,
      height: float
) -> int:
      bmi = weight / ((height / 100) ** 2)

      if (bmi < 18.5): return 0
      elif (bmi < 23): return 1
      elif (bmi < 25): return 2
      elif (bmi < 30): return 3
      else: return 4

'''
Huyết áp:
- 0: Huyết áp thấp
- 1: Bình thường
- 2: Tiền tăng huyết áp
- 3: Tăng huyết áp độ 1
- 4: Tăng huyết áp độ 2
'''
def classify_blood_pressure(
      sys: int,
      dia: int
) -> int:
      if (sys >= 160 or dia >= 100):
            return 4
      elif ((140 <= sys <= 159) or (90 <= dia <= 99)):
            return 3
      elif ((120 <= sys <= 139) or (80 <= dia <= 89)):
            return 2
      elif (sys < 90 or dia < 60):
            return 0
      else: return 1

'''
0: Tụt đường huyết
1: Bình thường
2: Tiền tiểu đường
3: Tiểu đường
'''
def classify_diabete(
      time: int,
      glycemic_index: int
) -> int:
      if (glycemic_index < 70): return 0
      else:
            if (time == 0):
                  if (glycemic_index < 100): return 1
                  elif (glycemic_index < 125): return 2
                  else: return 3
            if (time == 1):
                  if (glycemic_index < 140): return 1
                  elif (glycemic_index < 200): return 2
                  else: return 3
            if (time == 2):
                  if (glycemic_index < 140): return 1
                  else: return 2
            return 1
                  
'''
0: Bình thường
1: Dưới mức trung bình
2: Đáng báo động
3: Khẩn cấp
'''
def classify_lack_oxygen(
      spo2_index: int
) -> int:
      if (spo2_index < 90): return 3
      elif (spo2_index <= 93): return 2
      elif (spo2_index <= 97): return 1
      else: return 0

BMI_LABELS = {
    0: {"status": "Nhẹ cân", "level": "warning", "risk": "Nguy cơ thiếu vi chất, suy nhược cơ thể và giảm miễn dịch."},
    1: {"status": "Bình thường", "level": "good", "risk": "Thể trạng chuẩn, nguy cơ sức khỏe thấp."},
    2: {"status": "Tiền béo phì", "level": "warning", "risk": "Nguy cơ tích mỡ nội tạng, bắt đầu gia tăng tải trọng lên tim mạch và khớp."},
    3: {"status": "Béo phì độ I", "level": "danger", "risk": "Nguy cơ cao mắc rối loạn lipid máu, tăng huyết áp, gan nhiễm mỡ."},
    4: {"status": "Béo phì độ II", "level": "critical", "risk": "Rất nguy hiểm, áp lực lớn lên khớp gối, nguy cơ tim mạch và tiểu đường rất cao."}
}

BP_LABELS = {
    0: {"status": "Huyết áp thấp", "level": "warning", "risk": "Dễ chóng mặt, hoa mắt, choáng váng khi thay đổi tư thế hoặc tập luyện cường độ cao."},
    1: {"status": "Bình thường", "level": "good", "risk": "Huyết áp ổn định, tuần hoàn máu khỏe mạnh."},
    2: {"status": "Tiền tăng huyết áp", "level": "warning", "risk": "Cần lưu ý kiểm soát muối trong khẩu phần, tránh stress kéo dài."},
    3: {"status": "Tăng huyết áp độ 1", "level": "danger", "risk": "Áp lực mạch máu tăng cao, cần hạn chế bài tập nín thở, gánh tạ quá nặng."},
    4: {"status": "Tăng huyết áp độ 2", "level": "critical", "risk": "Nguy cơ tai biến và đột quỵ tim mạch, cần nghỉ ngơi và thăm khám y tế ngay."}
}

DIABETE_LABELS = {
    0: {"status": "Tụt đường huyết", "level": "danger", "risk": "Cơ thể cạn kiệt năng lượng, dễ ngất xỉu hoặc bủn rủn tay chân khi vận động."},
    1: {"status": "Bình thường", "level": "good", "risk": "Khả năng chuyển hóa đường tốt, độ nhạy insulin bình thường."},
    2: {"status": "Tiền tiểu đường", "level": "warning", "risk": "Kháng insulin nhẹ, cần hạn chế tinh bột hấp thu nhanh và đường tinh luyện."},
    3: {"status": "Tiểu đường", "level": "critical", "risk": "Lượng đường huyết trong máu cao, cần thực đơn kiểm soát GI nghiêm ngặt và theo dõi y tế."}
}

SPO2_LABELS = {
    0: {"status": "Bình thường", "level": "good", "risk": "Nồng độ oxy bão hòa trong máu tuyệt vời (98-100%)."},
    1: {"status": "Dưới mức trung bình", "level": "warning", "risk": "Oxy máu hơi thấp (94-97%), chú ý hít thở sâu, phòng ốc thông thoáng khi tập."},
    2: {"status": "Đáng báo động", "level": "danger", "risk": "Thiếu oxy mô (90-93%), giảm cường độ vận động ngay lập tức."},
    3: {"status": "Khẩn cấp", "level": "critical", "risk": "Thiếu oxy nghiêm trọng (<90%), cần được hỗ trợ y tế hoặc thở oxy."}
}

async def medical_checkup(
      weight: float = None,
      height: float = None,
      sys: int = None,
      dia: int = None,
      time: int = None,
      glycemic_index: int = None,
      spo2_index: int = None
) -> dict:
      bmi_code = classify_BMI(weight, height) if (weight is not None and height is not None) else None
      bp_code = classify_blood_pressure(sys, dia) if (sys is not None and dia is not None) else None
      diabete_code = classify_diabete(time, glycemic_index) if (time is not None and glycemic_index is not None) else None
      spo2_code = classify_lack_oxygen(spo2_index) if (spo2_index is not None) else None

      details = {}
      recommendations = {
          "workout_advice": [],
          "diet_advice": [],
          "general_risks": []
      }

      if bmi_code is not None:
          bmi_val = round(weight / ((height / 100) ** 2), 1)
          meta = BMI_LABELS.get(bmi_code)
          details["bmi"] = {
              "code": bmi_code,
              "value": bmi_val,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if bmi_code in [2, 3, 4]:
              recommendations["workout_advice"].append("Tăng cường các bài tập cardio ít tác động khớp (đạp xe, đi bộ nhanh, bơi) để giảm tải cho khớp gối.")
              recommendations["diet_advice"].append("Ưu tiên thực đơn giảm thâm hụt calo nhẹ và tăng tỷ trọng protein, rau xanh.")
          elif bmi_code == 0:
              recommendations["workout_advice"].append("Tập trung vào kháng lực hypertrophy nhẹ nhàng, hạn chế cardio tiêu hao quá nhiều calo.")
              recommendations["diet_advice"].append("Bổ sung thêm calo thặng dư giàu dinh dưỡng (các loại hạt, quả bơ, cơm gạo lứt).")

      if bp_code is not None:
          meta = BP_LABELS.get(bp_code)
          details["blood_pressure"] = {
              "code": bp_code,
              "sys": sys,
              "dia": dia,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if bp_code in [3, 4]:
              recommendations["workout_advice"].append("Tránh tuyệt đối các bài tập nín thở tăng áp lực khoang ngực (như tạ nặng tối đa), ưu tiên bài tập giãn cơ và nhịp thở đều.")
              recommendations["diet_advice"].append("Giảm tối đa lượng natri/muối trong đồ ăn, tránh thực phẩm chế biến sẵn.")
          elif bp_code == 0:
              recommendations["workout_advice"].append("Khởi động kỹ trước khi tập, chuyển tư thế từ nằm sang đứng chậm rãi để tránh hạ huyết áp tư thế.")
              recommendations["diet_advice"].append("Uống đủ nước và bổ sung thêm điện giải.")

      if diabete_code is not None:
          meta = DIABETE_LABELS.get(diabete_code)
          details["diabete"] = {
              "code": diabete_code,
              "value": glycemic_index,
              "time": time,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if diabete_code in [2, 3]:
              recommendations["workout_advice"].append("Đi bộ 10-15 phút nhẹ nhàng sau bữa ăn để kích hoạt cơ bắp hấp thu glucose tự nhiên.")
              recommendations["diet_advice"].append("Chọn thực phẩm có chỉ số đường huyết thấp (Low GI), thay thế đồ ngọt bằng yến mạch, đậu và rau họ cải.")
          elif diabete_code == 0:
              recommendations["diet_advice"].append("Luôn mang theo một chút kẹo ngọt hoặc trái cây đề phòng tụt đường huyết khi tập luyện.")

      if spo2_code is not None:
          meta = SPO2_LABELS.get(spo2_code)
          details["spo2"] = {
              "code": spo2_code,
              "value": spo2_index,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if spo2_code in [1, 2, 3]:
              recommendations["workout_advice"].append("Thời gian nghỉ giữa các hiệp tập cần kéo dài hơn bình thường để nhịp tim và oxy phục hồi.")

      return {
          "codes": [bmi_code, bp_code, diabete_code, spo2_code],
          "details": details,
          "recommendations": recommendations
      }

      if bmi_code is not None:
          bmi_val = round(weight / ((height / 100) ** 2), 1)
          meta = BMI_LABELS.get(bmi_code)
          details["bmi"] = {
              "code": bmi_code,
              "value": bmi_val,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if bmi_code in [2, 3, 4]:
              recommendations["workout_advice"].append("Tăng cường các bài tập cardio ít tác động khớp (đạp xe, đi bộ nhanh, bơi) để giảm tải cho khớp gối.")
              recommendations["diet_advice"].append("Ưu tiên thực đơn giảm thâm hụt calo nhẹ và tăng tỷ trọng protein, rau xanh.")
          elif bmi_code == 0:
              recommendations["workout_advice"].append("Tập trung vào kháng lực hypertrophy nhẹ nhàng, hạn chế cardio tiêu hao quá nhiều calo.")
              recommendations["diet_advice"].append("Bổ sung thêm calo thặng dư giàu dinh dưỡng (các loại hạt, quả bơ, cơm gạo lứt).")

      if bp_code is not None:
          meta = BP_LABELS.get(bp_code)
          details["blood_pressure"] = {
              "code": bp_code,
              "sys": sys,
              "dia": dia,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if bp_code in [3, 4]:
              recommendations["workout_advice"].append("Tránh tuyệt đối các bài tập nín thở tăng áp lực khoang ngực (như tạ nặng tối đa), ưu tiên bài tập giãn cơ và nhịp thở đều.")
              recommendations["diet_advice"].append("Giảm tối đa lượng natri/muối trong đồ ăn, tránh thực phẩm chế biến sẵn.")
          elif bp_code == 0:
              recommendations["workout_advice"].append("Khởi động kỹ trước khi tập, chuyển tư thế từ nằm sang đứng chậm rãi để tránh hạ huyết áp tư thế.")
              recommendations["diet_advice"].append("Uống đủ nước và bổ sung thêm điện giải.")

      if diabete_code is not None:
          meta = DIABETE_LABELS.get(diabete_code)
          details["diabete"] = {
              "code": diabete_code,
              "value": glycemic_index,
              "time": time,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if diabete_code in [2, 3]:
              recommendations["workout_advice"].append("Đi bộ 10-15 phút nhẹ nhàng sau bữa ăn để kích hoạt cơ bắp hấp thu glucose tự nhiên.")
              recommendations["diet_advice"].append("Chọn thực phẩm có chỉ số đường huyết thấp (Low GI), thay thế đồ ngọt bằng yến mạch, đậu và rau họ cải.")
          elif diabete_code == 0:
              recommendations["diet_advice"].append("Luôn mang theo một chút kẹo ngọt hoặc trái cây đề phòng tụt đường huyết khi tập luyện.")

      if spo2_code is not None:
          meta = SPO2_LABELS.get(spo2_code)
          details["spo2"] = {
              "code": spo2_code,
              "value": spo2_index,
              "status": meta["status"],
              "level": meta["level"],
              "risk": meta["risk"]
          }
          if spo2_code in [1, 2, 3]:
              recommendations["workout_advice"].append("Thời gian nghỉ giữa các hiệp tập cần kéo dài hơn bình thường để nhịp tim và oxy phục hồi.")

      return {
          "codes": [bmi_code, bp_code, diabete_code, spo2_code],
          "details": details,
          "recommendations": recommendations
      }

