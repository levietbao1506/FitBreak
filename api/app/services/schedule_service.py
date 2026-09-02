import pandas as pd
from pathlib import Path
from api.app.core.exceptions import InvalidSchedule

# Load database cache 1 lần duy nhất ở cấp module
DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "Exercise_Database.csv"
DF_EXERCISES_CACHE = pd.read_csv(DATA_PATH)


def filter_exercises(user_information: dict) -> pd.DataFrame:
    exercise_lv_vn = user_information.get("level_of_physical_activity")
    
    lv_mapping = {
        0: "heavy",
        1: "medium",
        2: "light"
    }
    exercise_lv_en = lv_mapping.get(exercise_lv_vn, exercise_lv_vn)
    
    return DF_EXERCISES_CACHE[
        DF_EXERCISES_CACHE["level of physical activity"] == exercise_lv_en
    ]


def determine_block_type(aim: int, res_cnt: int, cardio_cnt: int, pilate_cnt: int) -> str:
    """Xác định loại bài tập dựa trên mục tiêu (AIM) và số buổi đã phân bổ."""
    if aim == 0:
        counts = {"resistance_training": res_cnt, "cardio": cardio_cnt}
        return min(counts, key=counts.get)
    
    elif aim == 1:
        # Ưu tiên đủ 3 buổi resistance training trước, sau đó lấp cardio
        if res_cnt < 3:
            return "resistance_training"
        return "cardio"
    
    elif aim == 2:
        # Cân bằng cả 3 bộ môn
        counts = {
            "resistance_training": res_cnt,
            "cardio": cardio_cnt,
            "pilates": pilate_cnt
        }
        return min(counts, key=counts.get)
    
    return "cardio"


def select_exercises_for_slot(available_exercises: pd.DataFrame, time_budget: int) -> tuple[list[dict], int]:
    """Chọn danh sách bài tập vừa vặn với quỹ thời gian của slot."""
    if available_exercises.empty or time_budget <= 0:
        return [], 0

    selected = []
    current_time = 0
    shuffled = available_exercises.sample(frac=1).to_dict(orient="records")

    for row in shuffled:
        ex_time = int(row["time_need"])
        if current_time + ex_time <= time_budget:
            selected.append(row)
            current_time += ex_time

    return selected, current_time


async def schedule_maker(user_information: dict) -> dict:
    aim = user_information.get("aim", 0)
    timetable = user_information.get("timetable", {})
    valid_exercises = filter_exercises(user_information)

    resistance_cnt = cardio_cnt = pilate_cnt = 0
    generated_schedule = {}
    last_day_trained = False  # Cờ kiểm soát tập sole theo ngày

    for day, slots in timetable.items():
        if not isinstance(slots, list):
            slots = [slots]

        generated_schedule[day] = []
        is_today_trained = False

        for time_budget in slots:
            # Nếu quỹ thời gian <= 0 hoặc ngày hôm trước ĐÃ TẬP -> ép nghỉ slot này
            if time_budget <= 0 or last_day_trained:
                generated_schedule[day].append({
                    "day_type": "Rest",
                    "total_time": 0,
                    "slot_budget": time_budget,
                    "exercises": []
                })
                continue

            # 1. Chọn loại bài tập cho slot này
            block_type = determine_block_type(aim, resistance_cnt, cardio_cnt, pilate_cnt)

            # 2. Lọc và bốc bài tập phù hợp thời gian
            available = valid_exercises[valid_exercises["type"] == block_type]
            selected_exercises, total_time = select_exercises_for_slot(available, time_budget)

            # 3. Đóng gói kết quả & cập nhật counter
            if selected_exercises:
                if block_type == "resistance_training":
                    resistance_cnt += 1
                elif block_type == "cardio":
                    cardio_cnt += 1
                elif block_type == "pilates":
                    pilate_cnt += 1

                is_today_trained = True

                generated_schedule[day].append({
                    "day_type": block_type,
                    "total_time": total_time,
                    "slot_budget": time_budget,
                    "exercises": selected_exercises
                })
            else:
                generated_schedule[day].append({
                    "day_type": "Rest",
                    "total_time": 0,
                    "slot_budget": time_budget,
                    "exercises": []
                })

        # Cập nhật trạng thái cho ngày kế tiếp (hôm nay có tập -> mai nghỉ)
        last_day_trained = is_today_trained

    # Kiểm tra đảm bảo đúng số lượng aim, nếu không đủ thì raise exception
    if aim == 0 and (resistance_cnt < 3 or cardio_cnt < 3):
        raise InvalidSchedule(f"Thời gian tập không đủ để đảm bảo ít nhất 3 buổi kháng lực và 3 buổi cardio (hiện có: {resistance_cnt} kháng lực, {cardio_cnt} cardio).")
    elif aim == 1 and resistance_cnt < 3:
        raise InvalidSchedule(f"Thời gian tập không đủ để đảm bảo ít nhất 3 buổi kháng lực (hiện có: {resistance_cnt} kháng lực).")
    elif aim == 2 and (resistance_cnt < 2 or cardio_cnt < 2 or pilate_cnt < 2):
        raise InvalidSchedule(f"Thời gian tập không đủ để đảm bảo ít nhất 2 kháng lực, 2 cardio, 2 pilates (hiện có: {resistance_cnt} kháng lực, {cardio_cnt} cardio, {pilate_cnt} pilates).")

    return generated_schedule

''' Phụ lục
Đối với level of physical activity:
    0: Nặng
    1: Vừa
    2: Nhẹ

Đối với aim:
    0: Giảm cân
    1: Tăng cơ
    2: Duy trì
'''