from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, status
import pandas as pd

try:
    from app.core.auth import get_current_user
    from app.core.token_authorization import tokenAuthorization, token_authorization
    from app.schemas.exerciseLog import exerciseLog
except ImportError:
    from api.app.core.auth import get_current_user
    from api.app.core.token_authorization import tokenAuthorization, token_authorization
    from api.app.schemas.exerciseLog import exerciseLog

router = APIRouter()

# Tải cơ sở dữ liệu bài tập
EXERCISE_DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "Exercise_Database.csv"
try:
    DF_EXERCISES = pd.read_csv(EXERCISE_DATA_PATH)
except Exception:
    DF_EXERCISES = pd.DataFrame()


@router.get("/get-exercises")
async def get_exercises(request: Request, current_user: dict = Depends(get_current_user)):
    """Lấy toàn bộ danh sách bài tập khả dụng."""
    if DF_EXERCISES.empty:
        return {"success": True, "data": []}

    exercises = []
    for idx, row in DF_EXERCISES.iterrows():
        exercises.append({
            "id": idx + 1,
            "exercise": row.get("exercise"),
            "type": row.get("type"),
            "level_of_physical_activity": row.get("level of physical activity"),
            "time_need": int(row.get("time_need", 0)),
            "body_part": row.get("body_part"),
        })
    return {"success": True, "data": exercises}


@router.get("/get-exercises/{id}")
async def get_exercise_by_id(request: Request, id: int, current_user: dict = Depends(get_current_user)):
    """Lấy chi tiết một bài tập theo ID."""
    if DF_EXERCISES.empty or id < 1 or id > len(DF_EXERCISES):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bài tập không tồn tại")

    row = DF_EXERCISES.iloc[id - 1]
    return {
        "success": True,
        "data": {
            "id": id,
            "exercise": row.get("exercise"),
            "type": row.get("type"),
            "level_of_physical_activity": row.get("level of physical activity"),
            "time_need": int(row.get("time_need", 0)),
            "body_part": row.get("body_part"),
        },
    }


@router.post("/exercises-log")
async def exercises_log(
    request: Request,
    data: exerciseLog,
    token: tokenAuthorization = Depends(token_authorization),
):
    """Ghi nhận bài tập đã hoàn thành và cộng thưởng coins."""
    try:
        response = token.client.table("stats").select("*").eq("id", token.user_id).single().execute()
        stat = response.data

        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bản ghi stats của người dùng")

        final_coins = stat.get("coins", 0) + data.reward_coins

        token.client.table("exercise_logs").insert({
            "id": token.user_id,
            "exercise_id": data.exercise_id,
            "completed_at": data.completed_at.isoformat(),
            "reward_coins": data.reward_coins,
        }).execute()

        token.client.table("stats").update({
            "coins": final_coins,
        }).eq("id", token.user_id).execute()

        return {
            "success": True,
            "message": "Ghi nhận bài tập thành công",
            "coins": final_coins,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))