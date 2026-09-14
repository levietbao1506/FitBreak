from fastapi import HTTPException, status

def get_item_category(item_name: str) -> str:
    name_lower = (item_name or "").lower()
    if "background" in name_lower:
        return "background"
    if "hair" in name_lower:
        return "hair"
    if "shirt" in name_lower:
        return "shirt"
    if "skin" in name_lower:
        return "skin"
    return "weapon"


async def purchase_item(user_id: str, item_id: int, token):
    client = token.client

    item_res = client.table("item").select("*").eq("item_id", item_id).single().execute()
    item = item_res.data
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vật phẩm không tồn tại")

    price = item.get("price", 0)

    stats_res = client.table("stats").select("coins").eq("id", user_id).single().execute()
    stats = stats_res.data
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dữ liệu người chơi")

    current_coins = stats.get("coins", 0)
    if current_coins < price:
        return {"success": False, "message": "Không đủ Coin để mua vật phẩm này"}

    remaining_coin = current_coins - price

    client.table("stats").update({"coins": remaining_coin}).eq("id", user_id).execute()

    category = get_item_category(item.get("name"))
    client.table("user").upsert({
        "user_id": user_id,
        category: item.get("name")
    }).execute()

    return {
        "success": True,
        "message": f"Mua {item.get('name')} thành công",
        "remaining_coin": remaining_coin,
        "equipped_category": category,
        "equipped_item": item.get("name")
    }