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

@router.post("/exercises-log")
async def exercisesLog(request: Request, data: exerciseLog,
                       token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("stats").select("*").eq("user_id", token.user_id).single().execute()
        stat = response.data
        
        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        current_coins = stat.get("coins")
        if current_coins is None:
            current_coins = 0

        final_coins = current_coins + data.reward_coins

        token.client.table("stats").update({
            "coins" : final_coins
        }).eq("user_id" , token.user_id).execute()
        
        return {"message": "Success", "new_coins": final_coins}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))