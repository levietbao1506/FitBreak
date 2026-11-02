from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schedule import schedule
from app.core.token_authorization import tokenAuthorization, token_authorization
from app.services.schedule_service import schedule_maker

router = APIRouter()

@router.post("/schedule-maker")
async def scheduleMaker(inp: dict,
                        token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("profiles").select("*").eq("id", token.user_id).execute()
        stat = response.data[0]
        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        goal = stat.get("goal")
        if goal == "giảm cân": 
            goal = 0
        elif goal == "tăng cơ":
            goal = 1
        else:
            goal = 2

        # Lấy trực tiếp level_of_physical_activity từ bảng profiles (đã được phân loại dựa trên sức khỏe / BMI)
        # Giá trị lưu trong DB là text: 'heavy', 'medium', hoặc 'light'
        level_of_physical_activity = stat.get("level_of_physical_activity")
        
        # Nếu cột này còn NULL (user cũ chưa cập nhật), fallback theo BMI hoặc activity_frequency
        if not level_of_physical_activity:
            bmi = stat.get("bmi")
            weight = stat.get("weight")
            height = stat.get("height")
            if bmi is None and weight and height and height > 0:
                bmi = weight / ((height / 100) ** 2)

            if bmi is not None:
                if 18.5 <= bmi < 23.0:
                    level_of_physical_activity = "heavy"
                elif 23.0 <= bmi < 25.0:
                    level_of_physical_activity = "medium"
                else:
                    level_of_physical_activity = "light"
            else:
                act_freq = stat.get("activity_frequency")
                if act_freq == 3:
                    level_of_physical_activity = "heavy"
                elif act_freq == 2:
                    level_of_physical_activity = "medium"
                else:
                    level_of_physical_activity = "light"

        user_info = {
            "timetable": inp,
            "level_of_physical_activity": level_of_physical_activity,
            "aim": goal
        }

        result = await schedule_maker(user_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
