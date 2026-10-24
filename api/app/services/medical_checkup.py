'''
BMI:
- 0: Nhẹ cân
- 1: Bình thường
- 2: Tiền béo phì
- 3: Béo phì độ I
- 4: Béo phù độ II
'''
def classify_BMI(
      weight: float,
      height: float
) -> int:
      bmi = weight / (height ^ 2)

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

async def medical_checkup(
      weight: float,
      height: float,
      sys: int,
      dia: int,
      time: int,
      glycemic_index: int,
      spo2_index: int
) -> list:
      return [
            classify_BMI(weight, height),
            classify_blood_pressure(sys, dia),
            classify_diabete(time, glycemic_index),
            classify_lack_oxygen(spo2_index)
      ]

