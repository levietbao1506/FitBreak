from math import ceil


def calculateBMI(weight: float, height: float) -> float:
    """
    Tính chỉ số khối cơ thể (BMI).
    weight: cân nặng (kg)
    height: chiều cao (cm)
    """
    if height <= 0:
        raise ValueError("Chiều cao phải lớn hơn 0")
    if weight <= 0:
        raise ValueError("Cân nặng phải lớn hơn 0")

    height_in_meter = height / 100.0
    bmi = weight / (height_in_meter ** 2)
    return round(bmi, 1)


def calculateBMR(weight: float, height: float, age: int, gender: bool) -> int:
    """
    Tính tỉ lệ trao đổi chất cơ bản (BMR) theo công thức Mifflin-St Jeor.
    gender: True (Nam) / False (Nữ)
    """
    if height <= 0 or weight <= 0 or age <= 0:
        raise ValueError("Chiều cao, cân nặng và tuổi phải lớn hơn 0")

    if gender:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return ceil(bmr)


def calculateTDEE(bmr: int, activity_frequency: int) -> int:
    """
    Tính tổng năng lượng tiêu thụ hàng ngày (TDEE).
    activity_frequency:
      1: Ít vận động -> 1.2
      2: Vận động nhẹ/vừa (1-4 buổi/tuần) -> 1.375
      3: Vận động nhiều (5-6 buổi/tuần) -> 1.638
    """
    if activity_frequency == 1:
        r = 1.2
    elif activity_frequency == 2:
        r = 1.375
    else:
        r = 1.638

    return ceil(bmr * r)