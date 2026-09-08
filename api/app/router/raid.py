from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.updateBossHealth import updateBossHealth
from app.schemas.defeatBoss import defeatBoss
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

@router.update("/update-boss-health")
async def updateBossHealth(data: updateBossHealth,
                           token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("raid").select("*").eq(data.team, "team").single().execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not exist")
        old_boss_health = stat["health"]
        new_boss_health = old_boss_health - data.damage
        if new_boss_health < 0:
            new_boss_health = 0

        token.client.table("raid").update({
            "health" : new_boss_health
        }).eq("team", data.team).execute()

        return {"message" : "Update boss health"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.update("/defeat_boss")
async def defeatBoss(data: defeatBoss,
                     token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("raid").select("*").eq(data.team, "team").single().execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not exist")
        new_boss_id = stat["boss_id"] + 1 if stat["boss_id"] + 1 <= 5 else 5
        response_boss = token.client.table("boss").select("*").eq("id", new_boss_id).single().execute()
        boss_stat = response_boss.data
        if not boss_stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boss not exist")
        token.client.table("raid").update({
            "boss_id" : boss_stat["id"],
            "boss_name" : boss_stat["name"],
            "health" : boss_stat["health"],
            "reward_coins" : boss_stat["reward_coins"]
        }).eq("team", data.team)

        return {"Message" : "Boss defeated"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))