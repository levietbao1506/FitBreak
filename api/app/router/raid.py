from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.updateBossHealth import updateBossHealth
from app.schemas.defeatBoss import defeatBoss
from app.core.token_authorization import tokenAuthorization, token_authorization
from app.services.raid_service import apply_boss_damage, advance_to_next_boss

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
        result = apply_boss_damage(token.client, data.team, data.damage)
        return {"message": "Update boss health success", **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/defeat_boss")
async def defeatBoss(data: defeatBoss,
                     token: tokenAuthorization = Depends(token_authorization)):
    try:
        result = advance_to_next_boss(token.client, data.team)
        reward = result["reward_coins"]
        return {
            "message": f"Boss defeated! All team members received {reward} coins.",
            "next_boss": result["next_boss"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))