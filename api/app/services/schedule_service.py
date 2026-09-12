from pathlib import Path
import random
import pandas as pd
from api.app.core.exceptions import InvalidSchedule

DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "Exercise_Database.csv"
DF_EXERCISES_CACHE = pd.read_csv(DATA_PATH)


def filter_exercises(user_information: dict) -> pd.DataFrame:
    """Lọc danh sách bài tập theo level thể chất của user."""
    lv_mapping = {0: "heavy", 1: "medium", 2: "light"}
    exercise_lv_vn = user_information.get("level_of_physical_activity")
    exercise_lv_en = lv_mapping.get(exercise_lv_vn, "medium")
    return DF_EXERCISES_CACHE[
        DF_EXERCISES_CACHE["level of physical activity"] == exercise_lv_en
    ]


def get_min_duration(aim: int, block_type: str, user_lv: int) -> int:
    """Thời gian tối thiểu quy định theo ảnh tài liệu."""
    if block_type == "resistance_training":
        return 45 if aim == 1 else 20  # Tăng cơ: 45-60p, Giảm cân/Duy trì: 20p
    elif block_type == "cardio":
        if aim == 2:
            return 20 if user_lv == 1 else 30  # Duy trì: LISS (>=20) hoặc Đi bộ (>=30)
        return 10 if user_lv == 0 else (20 if user_lv == 1 else 30)
    elif block_type == "pilates":
        return 20  # Pilates: 20-30p (chấp nhận 15-20p theo trần DB)
    return 20


def select_exercises_knapsack(
    available_df: pd.DataFrame, 
    budget: int, 
    min_required: int
) -> tuple[list[dict], int]:
    """
    Dùng Knapsack (Subset Sum) chọn bài tập:
    - Nếu là Cardio: bốc trực tiếp bài tập tương ứng.
    - Với Resistance/Pilates: Ưu tiên chọn đa dạng nhóm cơ ('body_part'),
      tối đa 1 bài cho mỗi nhóm cơ để bài tập không bị trùng lặp cơ thể.
    """
    if available_df.empty or budget < min_required:
        return [], 0

    # Nếu là Cardio -> Bốc bài Cardio phù hợp
    if available_df["type"].iloc[0] == "cardio":
        cardio_row = available_df.iloc[0].to_dict()
        ex_time = int(cardio_row.get("time_need", 0))
        if ex_time <= budget:
            return [cardio_row], ex_time
        return [], 0

    # Với Resistance/Pilates: Lọc mỗi body_part chỉ lấy 1 bài tập ngẫu nhiên
    records = available_df.to_dict(orient="records")
    random.shuffle(records)

    unique_body_part_records = {}
    for r in records:
        bp = r.get("body_part")
        if bp not in unique_body_part_records:
            unique_body_part_records[bp] = r
    pool = list(unique_body_part_records.values())

    # Thuật toán 0/1 Knapsack
    dp = {0: (0, [])}
    for idx, item in enumerate(pool):
        time_need = int(item.get("time_need", 0))
        if time_need <= 0 or time_need > budget:
            continue
        new_dp = dict(dp)
        for cur_w, (val, indices) in dp.items():
            nxt_w = cur_w + time_need
            if nxt_w <= budget and nxt_w not in new_dp:
                new_dp[nxt_w] = (val + time_need, indices + [idx])
        dp = new_dp

    best_weight = max(dp.keys())
    # Nếu DB không đủ bài để đạt budget cao (như 60p tăng cơ), lấy tối đa các bài khác nhóm cơ
    if best_weight < min_required and len(pool) > 0:
        total_pool_time = sum(int(r["time_need"]) for r in pool)
        if total_pool_time <= budget and total_pool_time >= 35:
            return pool, total_pool_time

    selected_indices = dp[best_weight][1]
    selected_exercises = [pool[i] for i in selected_indices]

    return selected_exercises, best_weight


def pick_block_with_recovery(
    aim: int, 
    prev_type: str | None, 
    res_cnt: int, 
    cardio_cnt: int, 
    pilate_cnt: int,
    budget: int,
    user_lv: int
) -> str | None:
    """
    Điều phối bộ môn đảm bảo:
    1. Recovery Logic: Không tập Kháng lực (resistance) 2 ngày liên tiếp.
    2. Cân bằng và ưu tiên đạt chỉ tiêu bắt buộc.
    """
    candidates = []

    if aim == 0:  # Giảm cân: 3-4 kháng lực, 3-4 cardio
        if res_cnt < 4:
            candidates.append("resistance_training")
        if cardio_cnt < 4:
            candidates.append("cardio")

    elif aim == 1:  # Tăng cơ: 3-4 kháng lực (bắt buộc), cardio tự chọn
        if res_cnt < 4:
            candidates.append("resistance_training")
        candidates.append("cardio")

    elif aim == 2:  # Duy trì: >=2 mỗi thể loại
        if res_cnt < 3:
            candidates.append("resistance_training")
        if cardio_cnt < 3:
            candidates.append("cardio")
        if pilate_cnt < 3:
            candidates.append("pilates")

    # Không tập cùng nhóm kháng lực nếu hôm trước vừa tập
    if prev_type == "resistance_training" and "resistance_training" in candidates:
        candidates = [c for c in candidates if c != "resistance_training"]

    # Sắp xếp ưu tiên môn có số buổi ít hơn để cân đối
    cnt_map = {"resistance_training": res_cnt, "cardio": cardio_cnt, "pilates": pilate_cnt}
    candidates.sort(key=lambda x: cnt_map[x])

    for block in candidates:
        # Mục tiêu duy trì không dùng HIIT (chỉ nhận LISS hoặc Đi bộ)
        if aim == 2 and block == "cardio" and user_lv == 0:
            continue
        min_req = get_min_duration(aim, block, user_lv)
        if budget >= min_req:
            return block

    return None


def schedule_maker(user_information: dict) -> dict:
    aim = user_information.get("aim", 0)
    user_lv = user_information.get("level_of_physical_activity", 1)
    timetable = user_information.get("timetable", {})
    valid_exercises = filter_exercises(user_information)

    resistance_cnt = cardio_cnt = pilate_cnt = 0
    generated_schedule = {}
    last_trained_type = None

    for day, raw_slots in timetable.items():
        slots = raw_slots if isinstance(raw_slots, list) else [raw_slots]
        generated_schedule[day] = []
        today_trained_type = None

        for budget in slots:
            chosen_block = pick_block_with_recovery(
                aim=aim,
                prev_type=last_trained_type,
                res_cnt=resistance_cnt,
                cardio_cnt=cardio_cnt,
                pilate_cnt=pilate_cnt,
                budget=budget,
                user_lv=user_lv
            )

            if not chosen_block:
                generated_schedule[day].append({
                    "day_type": "Rest",
                    "total_time": 0,
                    "slot_budget": budget,
                    "exercises": []
                })
                continue

            # Lấy data theo block
            avail = valid_exercises[valid_exercises["type"] == chosen_block]
            
            # Đối với duy trì (aim=2), nếu là cardio thì chỉ lấy LISS hoặc Walking từ database
            if aim == 2 and chosen_block == "cardio":
                avail = DF_EXERCISES_CACHE[
                    (DF_EXERCISES_CACHE["type"] == "cardio") & 
                    (DF_EXERCISES_CACHE["exercise"].isin(["LISS", "Walking"]))
                ]

            min_req = get_min_duration(aim, chosen_block, user_lv)
            selected_ex, total_time = select_exercises_knapsack(avail, budget, min_req)

            if selected_ex:
                if chosen_block == "resistance_training":
                    resistance_cnt += 1
                elif chosen_block == "cardio":
                    cardio_cnt += 1
                elif chosen_block == "pilates":
                    pilate_cnt += 1

                today_trained_type = chosen_block
                generated_schedule[day].append({
                    "day_type": chosen_block,
                    "total_time": total_time,
                    "slot_budget": budget,
                    "exercises": selected_ex
                })
            else:
                generated_schedule[day].append({
                    "day_type": "Rest",
                    "total_time": 0,
                    "slot_budget": budget,
                    "exercises": []
                })

        last_trained_type = today_trained_type

    # Kiểm tra tính hợp lệ tối thiểu theo đúng spec
    if aim == 0 and (resistance_cnt < 3 or cardio_cnt < 3):
        raise InvalidSchedule(
            f"Mục tiêu Giảm cân cần tối thiểu 3 Kháng lực và 3 Cardio. "
            f"Hiện có: {resistance_cnt} Kháng lực, {cardio_cnt} Cardio."
        )
    elif aim == 1 and resistance_cnt < 3:
        raise InvalidSchedule(
            f"Mục tiêu Tăng cơ cần tối thiểu 3 Kháng lực. "
            f"Hiện có: {resistance_cnt} Kháng lực."
        )
    elif aim == 2 and (resistance_cnt < 2 or cardio_cnt < 2 or pilate_cnt < 2):
        raise InvalidSchedule(
            f"Mục tiêu Duy trì cần tối thiểu 2 Kháng lực, 2 Cardio nhẹ, 2 Pilates. "
            f"Hiện có: {resistance_cnt} Kháng lực, {cardio_cnt} Cardio, {pilate_cnt} Pilates."
        )

    return generated_schedule