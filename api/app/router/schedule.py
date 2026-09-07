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
        stat = response.data
        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        goal = stat["goal"]
        activity_frequency = stat["activity_frequency"]
        if goal == "giảm cân": 
            goal = 0
        elif goal == "tăng cơ":
            goal = 1
        else: goal = 2
        if activity_frequency == 3: 
            activity_frequency = 0
        elif activity_frequency == 2:
            activity_frequency = 1
        else: activity_frequency = 2

        data = schedule(
            timetable = inp,
            level_of_physical_activity = activity_frequency,
            aim = goal
        )

        result = schedule_maker(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))