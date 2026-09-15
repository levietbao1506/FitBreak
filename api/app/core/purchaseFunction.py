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


async def purchase_item(user_id: str, item_id: str | int, token):
    try:
        item_res = token.client.table("item").select("*").eq("item_id", item_id).execute()
        if not item_res.data:
            return {"success": False, "message": "Vật phẩm không tồn tại!"}
        
        item_data = item_res.data[0]
        item_price = item_data.get("price", 0)

        stats_res = token.client.table("stats").select("coins").eq("user_id", user_id).execute()
        if not stats_res.data:
            return {"success": False, "message": "Không tìm thấy dữ liệu stats của người dùng!"}
        
        current_coins = stats_res.data[0].get("coins", 0)

        if current_coins < item_price:
            return {"success": False, "message": "Bạn không đủ Coins!"}

        new_coins = current_coins - item_price
        token.client.table("stats").update({"coins": new_coins}).eq("user_id", user_id).execute()

        return {
            "success": True,
            "message": "Mua hàng thành công!",
            "remaining_coin": new_coins
        }
    except Exception as e:
        print(f"Lỗi trong purchase_item: {e}")
        return {"success": False, "message": f"Lỗi hệ thống: {str(e)}"}