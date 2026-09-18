from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from app.core.auth import get_current_user
from app.schemas.exerciseLog import exerciseLog
from app.core.token_authorization import token_authorization, tokenAuthorization
from app.services.raid_service import apply_boss_damage

router = APIRouter()

@router.get("/get-exercises")
async def getExercises(request: Request, current_user: dict = Depends(get_current_user)):
    pass

@router.get("/get-exercises/{id}")
async def getExercisesById(request: Request, id: int,
                           current_user: dict = Depends(get_current_user)):
    pass

@router.post("/exercises-log")
async def exercisesLog(request: Request, data: exerciseLog,
                       token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("stats").select("*").eq("user_id", token.user_id).single().execute()
        stat = response.data

        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        current_coins = stat.get("coins") or 0
        final_coins = current_coins + data.reward_coins

        token.client.table("stats").update({
            "coins": final_coins
        }).eq("user_id", token.user_id).execute()

        # ---- Trừ máu boss dựa trên team + damage của user ----
        boss_result = None
        team = stat.get("team")
        damage = stat.get("damage") or stat.get("str") or 0

        if team and damage > 0:
            boss_result = apply_boss_damage(token.client, team, damage)

        return {
            "message": "Success",
            "new_coins": final_coins,
            "boss": boss_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))