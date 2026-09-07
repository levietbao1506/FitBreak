from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.updateBossHealth import updateBossHealth
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

@router.update("/update-boss-health")
async def updateBossHealth(data: updateBossHealth,
                           token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("raid").select("*").eq(data.team, "team").single(). execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not exist")
        old_boss_health = stat["health"]
        new_boss_health = old_boss_health - data.damage
        if new_boss_health < 0:
            new_boss_health = 0

        if new_boss_health > 0:
            token.client.table("raid").update({
                "health" : new_boss_health
            }).eq("team", data.team).execute()
        else:
            pass # update boss moi

        return {"message" : "Update boss health"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))