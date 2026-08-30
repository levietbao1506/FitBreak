from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from app.core.auth import get_current_user
from app.schemas.exerciseLog import exerciseLog
from app.core.token_authorization import token_authorization, tokenAuthorization

router = APIRouter()

@router.get("/get-exercises")
async def getExercises(request: Request, current_user: dict = Depends(get_current_user)):
    pass

@router.get("/get-exercises/{id}")
async def getExercisesById(request: Request, id: int,
                           current_user: dict = Depends(get_current_user)):
    pass

# gui du lieu da hoan thanh exercise
@router.post("/exercises-log")
async def exercisesLog(request: Request, data: exerciseLog,
                    token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("stats").select("*").eq("id", token.user_id).single().execute()
        stat = response.data
        final_coins = stat["coins"] + data.reward_coins

        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        token.client.table("exercise_logs").insert({
            "id" : token.user_id,
            "exercise_id" : data.exercise_id,
            "completed_at" : data.completed_at.isoformat(),
            "reward_coins" : data.reward_coins
        }).execute()

        token.client.table("stats").update({
            "coins" : final_coins
        }).eq("id" , token.user_id).execute()

        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))