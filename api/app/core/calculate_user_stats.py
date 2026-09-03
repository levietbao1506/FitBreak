from math import ceil

def calculateBMI(weight: float, height: int):
    heightInMeter = height / 100
    bmi = weight / (heightInMeter ** 2)
    return round(bmi, 1)

def calculateBMR(weight: float, height: int, age: int, gender: bool):
    bmr = None
    if gender:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    result = ceil(bmr)
    return result

# activity frequency:
# 1 : it hoat dong / lau lau moi hoat dong -> R = 1.2
# 2 : hoat dong 1 - 3 buoi 1 tuan -> R = 1.375
# 3 : hoat dong 4 - 5 buoi 1 tuan -> R = 1.55
# 4 : hoat dong 6 - 7 buoi 1 tuan -> R = 1.725
def calculateTDEE(bmr: int, activity_frequency: int):
    r = None
    if activity_frequency == 1:
        r = 1.2
    elif activity_frequency == 2:
        r = 1.375
    elif activity_frequency == 3:
        r = 1.55
    else: r = 1.725

    tdee = bmr * r
    result = ceil(tdee)
    return result

def main():
    height = 179
    weight = 67
    age = 16
    gender = True,
    activity_frequency = 2
    bmi = calculateBMI(weight, height)
    bmr = calculateBMR(weight, height, age, gender)
    tdee = calculateTDEE(bmr, activity_frequency)
    print(bmi, bmr, tdee)

if __name__ == "__main__":
    main()