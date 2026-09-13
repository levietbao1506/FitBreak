from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.updateBossHealth import updateBossHealth
from app.schemas.defeatBoss import defeatBoss
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

@router.post("/update-boss-health")
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

@router.post("/defeat_boss")
async def defeatBoss(data: defeatBoss,
                      token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("raid").select("*").eq("team", data.team).single().execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raid team not found")
        reward_coins = stat.get("reward_coins", 0)

        if reward_coins > 0:
            team_users_res = token.client.table("stats").select("id, coins").eq("team", data.team).execute()
            team_users = team_users_res.data or []

            for user in team_users:
                current_coins = user.get("coins") or 0
                updated_coins = current_coins + reward_coins
                
                token.client.table("stats").update({
                    "coins": updated_coins
                }).eq("id", user["id"]).execute()

        new_boss_id = stat["boss_id"] + 1 if stat["boss_id"] + 1 <= 1 else 1
        response_boss = token.client.table("boss").select("*").eq("id", new_boss_id).single().execute()
        boss_stat = response_boss.data
        if not boss_stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boss not exist")

        token.client.table("raid").update({
            "boss_id": boss_stat["id"],
            "boss_name": boss_stat["name"],
            "health": boss_stat["health"],
            "reward_coins": boss_stat["reward_coins"]
        }).eq("team", data.team).execute()

        return {"message": f"Boss defeated! All team members received {reward_coins} coins."}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))