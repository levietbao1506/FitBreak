from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.updateBossHealth import updateBossHealth
from app.schemas.defeatBoss import defeatBoss
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

IMAGE_MAPPING = {
    1: "quest_alligator.png",
    2: "quest_axolotl.png",
    3: "quest_chameleon.png",
    4: "quest_falcon.png",
    5: "quest_goldenknight3.png"
}

@router.get("/get-raid-boss/{team_name}")
async def get_raid_boss(team_name: str, token: tokenAuthorization = Depends(token_authorization)):
    try:
        try:
            team_id = int(team_name.replace("team", ""))
        except ValueError:
            team_id = 1

        raid_res = token.client.table("raid").select("*").eq("team", team_id).single().execute()
        raid_data = raid_res.data
        if not raid_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raid team not found")
        
        boss_id = raid_data.get("boss_id", 1)

        boss_res = token.client.table("boss").select("*").eq("id", boss_id).single().execute()
        boss_data = boss_res.data
        
        if not boss_data:
            boss_res = token.client.table("boss").select("*").order("id", desc=False).limit(1).execute()
            boss_data = boss_res.data[0] if boss_res.data else {}

        image_name = boss_data.get("image") or IMAGE_MAPPING.get(boss_data.get("id", 1), "quest_alligator.png")
        supabase_url = token.client.supabase_url
        image_url = f"{supabase_url}/storage/v1/object/public/boss/{image_name}"

        return {
            "boss_id": boss_data.get("id", 1),
            "boss_name": boss_data.get("name", "Unknown Boss"),
            "health": raid_data.get("health", 100), 
            "max_health": boss_data.get("health", 100),   
            "reward_coins": boss_data.get("reward_coins", 10),
            "image_url": image_url
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/update-boss-health")
async def updateBossHealth(data: updateBossHealth,
                           token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("raid").select("*").eq("team", data.team).single().execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raid team not found")
            
        old_boss_health = stat["health"]
        new_boss_health = max(0, old_boss_health - data.damage)

        token.client.table("raid").update({
            "health": new_boss_health
        }).eq("team", data.team).execute()

        return {
            "message": "Update boss health success",
            "current_health": new_boss_health
        }
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

        current_boss_id = stat.get("boss_id", 1)

        boss_res = token.client.table("boss").select("*").eq("id", current_boss_id).single().execute()
        current_boss_stat = boss_res.data
        reward_coins = current_boss_stat.get("reward_coins", 0) if current_boss_stat else stat.get("reward_coins", 0)

        if reward_coins > 0:
            team_users_res = token.client.table("stats").select("id, coins").eq("team", data.team).execute()
            team_users = team_users_res.data or []

            for user in team_users:
                current_coins = user.get("coins") or 0
                updated_coins = current_coins + reward_coins
                
                token.client.table("stats").update({
                    "coins": updated_coins
                }).eq("id", user["id"]).execute()

        next_boss_res = token.client.table("boss").select("*").gt("id", current_boss_id).order("id", desc=False).limit(1).execute()
        
        if not next_boss_res.data:
            next_boss_res = token.client.table("boss").select("*").order("id", desc=False).limit(1).execute()

        next_boss_stat = next_boss_res.data[0]

        token.client.table("raid").update({
            "boss_id": next_boss_stat["id"],
            "boss_name": next_boss_stat["name"],
            "health": next_boss_stat["health"],
            "reward_coins": next_boss_stat["reward_coins"]
        }).eq("team", data.team).execute()

        return {
            "message": f"Boss defeated! All team members received {reward_coins} coins.",
            "next_boss": {
                "id": next_boss_stat["id"],
                "name": next_boss_stat["name"],
                "health": next_boss_stat["health"],
                "reward_coins": next_boss_stat["reward_coins"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))