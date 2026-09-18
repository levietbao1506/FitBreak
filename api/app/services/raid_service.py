from fastapi import HTTPException, status


def advance_to_next_boss(client, team: int):
    """Phát thưởng coin cho cả team và chuyển sang boss tiếp theo."""
    raid_res = client.table("raid").select("*").eq("team", team).single().execute()
    raid = raid_res.data
    if not raid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raid team not found")

    current_boss_id = raid.get("boss_id", 1)

    boss_res = client.table("boss").select("*").eq("id", current_boss_id).single().execute()
    current_boss = boss_res.data
    reward_coins = current_boss.get("reward_coins", 0) if current_boss else raid.get("reward_coins", 0)

    if reward_coins > 0:
        team_users_res = client.table("stats").select("user_id, coins").eq("team", team).execute()
        team_users = team_users_res.data or []
        for user in team_users:
            current_coins = user.get("coins") or 0
            client.table("stats").update({
                "coins": current_coins + reward_coins
            }).eq("user_id", user["user_id"]).execute()

    next_boss_res = (client.table("boss").select("*")
                      .gt("id", current_boss_id).order("id", desc=False).limit(1).execute())
    if not next_boss_res.data:
        next_boss_res = client.table("boss").select("*").order("id", desc=False).limit(1).execute()
    next_boss = next_boss_res.data[0]

    client.table("raid").update({
        "boss_id": next_boss["id"],
        "boss_name": next_boss["name"],
        "health": next_boss["health"],
        "reward_coins": next_boss["reward_coins"]
    }).eq("team", team).execute()

    return {
        "boss_defeated": True,
        "reward_coins": reward_coins,
        "next_boss": {
            "id": next_boss["id"],
            "name": next_boss["name"],
            "health": next_boss["health"],
            "reward_coins": next_boss["reward_coins"]
        }
    }


def apply_boss_damage(client, team: int, damage: int):
    """Trừ máu boss theo damage. Nếu máu <= 0 -> tự động chuyển boss + thưởng coin."""
    raid_res = client.table("raid").select("*").eq("team", team).single().execute()
    raid = raid_res.data
    if not raid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raid team not found")

    old_health = raid.get("health", 0)
    new_health = old_health - damage

    if new_health > 0:
        client.table("raid").update({"health": new_health}).eq("team", team).execute()
        return {
            "boss_defeated": False,
            "current_health": new_health
        }

    # Máu <= 0 -> boss chết
    return advance_to_next_boss(client, team)