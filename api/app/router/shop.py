from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from app.core.token_authorization import token_authorization, tokenAuthorization
from app.schemas.purchase import PurchaseRequest
from app.core.purchaseFunction import purchase_item

router = APIRouter()

SHOP_ASSET_BUCKET = "user"

SHOP_ITEM_MAP = {
    "Autumn Bridge Background": "background_autumn_bridge.png",
    "Aurora Background": "background_aurora.png",
    "Animals Background": "background_animals_den.png",
    "Black Hair": "hair_bangs_1_black.png",
    "Red Hair": "hair_bangs_1_TRUred.png",
    "Peppermint Hair": "hair_bangs_3_peppermint.png",
    "Blue Shirt": "icon_broad_shirt_blue.png",
    "Fire Shirt": "icon_broad_shirt_fire.png",
    "Pink Shirt": "icon_broad_shirt_pink.png",
    "Zombie shirt": "icon_broad_shirt_zombie.png",
    "Orange Skin": "skin_f69922.png",
    "Black Skin": "skin_98461a.png",
    "Yellow Skin": "skin_f5d70f.png",
    "White Skin": "skin_ddc994.png",
    "Warrior Sword": "shop_weapon_warrior_5.png",
    "Lunar Scythe": "shop_weapon_special_lunarScythe.png",
    "Frost Sword": "shop_weapon_special_1.png",
    "Knight Sword": "shop_weapon_rogue_1.png",
    "Magic Staff": "shop_weapon_healer_6.png"
}

AVATAR_EQUIP_MAP = SHOP_ITEM_MAP

def get_supabase_image_url(client, file_name: str):
    if not file_name:
        return None
    try:
        return client.storage.from_(SHOP_ASSET_BUCKET).get_public_url(file_name)
    except Exception as e:
        print(f"Lỗi lấy URL ảnh từ Supabase: {e}")
        return None

def get_item_category(item_name: str) -> str:
    name_lower = (item_name or "").lower()
    if "background" in name_lower:
        return "background"
    if "skin" in name_lower:
        return "skin"
    if "shirt" in name_lower:
        return "shirt"
    if "hair" in name_lower:
        return "hair"
    return "weapon"

class EquipRequest(BaseModel):
    user_id: str
    item_id: Union[int, str]  # Chuẩn hóa kiểu dữ liệu int8 trong DB

@router.get("/items")
async def get_all_items(
    user_id: Optional[str] = None,
    token: tokenAuthorization = Depends(token_authorization)
):
    try:
        result = token.client.table("item").select("*").execute()
        items = result.data or []

        equipped_names = set()
        owned_names = set()

        if user_id:
            user_res = token.client.table("user").select("background, skin, shirt, hair, weapon, inventory").eq("user_id", user_id).execute()
            if user_res.data:
                u_data = user_res.data[0]
                equipped_names = {v for k, v in u_data.items() if k != "inventory" and v}
                owned_names = set(u_data.get("inventory") or [])

        for item in items:
            item_name = item.get("name")
            item_price = item.get("price", 0)

            item["image_url"] = get_supabase_image_url(token.client, SHOP_ITEM_MAP.get(item_name, item_name))
            item["equip_url"] = get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(item_name, item_name))

            item["is_equipped"] = item_name in equipped_names

            item["is_owned"] = (item_name in owned_names) or item["is_equipped"] or (item_price == 0)

        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/equipped-avatar/{user_id}")
async def get_user_equipped_avatar(user_id: str, token: tokenAuthorization = Depends(token_authorization)):
    try:
        user_res = token.client.table("user").select("*").eq("user_id", user_id).execute()
        user_data = user_res.data[0] if user_res.data else {}
        
        bg_name = user_data.get("background")
        skin_name = user_data.get("skin") or "Orange Skin"
        shirt_name = user_data.get("shirt") or "Blue Shirt"
        hair_name = user_data.get("hair") or "Black Hair"
        weapon_name = user_data.get("weapon")

        return {
            "head": None,
            "background": get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(bg_name, bg_name)),
            "skin": get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(skin_name, skin_name)),
            "shirt": get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(shirt_name, shirt_name)),
            "hair": get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(hair_name, hair_name)),
            "weapon": get_supabase_image_url(token.client, AVATAR_EQUIP_MAP.get(weapon_name, weapon_name)),
        }
    except Exception as e:
        return {
            "head": None,
            "background": None,
            "skin": get_supabase_image_url(token.client, "skin_f69922.png"),
            "shirt": get_supabase_image_url(token.client, "icon_broad_shirt_blue.png"),
            "hair": get_supabase_image_url(token.client, "hair_bangs_1_black.png"),
            "weapon": None,
        }

@router.post("/purchase")
async def purchase(request: PurchaseRequest, token: tokenAuthorization = Depends(token_authorization)):
    try:
        res = await purchase_item(request.user_id, request.item_id, token)

        if isinstance(res, dict) and res.get("success"):
            try:
                item_res = token.client.table("item").select("*").eq("item_id", request.item_id).execute()
                if item_res.data:
                    item_data = item_res.data[0]
                    item_name = item_data.get("name")
                    category = get_item_category(item_name)

                    user_res = token.client.table("user").select("inventory").eq("user_id", request.user_id).execute()
                    current_inv = []
                    if user_res.data and user_res.data[0].get("inventory"):
                        current_inv = user_res.data[0].get("inventory")

                    if item_name not in current_inv:
                        current_inv.append(item_name)

                    token.client.table("user").update({
                        "inventory": current_inv,
                        category: item_name
                    }).eq("user_id", request.user_id).execute()

            except Exception as e:
                print(f"Lỗi cập nhật kho đồ/trang bị: {e}")

        return res
    except Exception as e:
        print(f"Lỗi mua hàng Backend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/equip")
async def equip_item(request: EquipRequest, token: tokenAuthorization = Depends(token_authorization)):
    try:
        item_res = token.client.table("item").select("*").eq("item_id", request.item_id).execute()
        if not item_res.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy vật phẩm")

        item_data = item_res.data[0]
        item_name = item_data.get("name")
        item_price = item_data.get("price", 0)
        category = get_item_category(item_name)

        if item_price > 0:
            user_res = token.client.table("user").select("inventory").eq("user_id", request.user_id).execute()
            inventory = (user_res.data[0].get("inventory") or []) if user_res.data else []
            if item_name not in inventory:
                raise HTTPException(status_code=400, detail="Bạn chưa sở hữu vật phẩm này!")

        token.client.table("user").update({category: item_name}).eq("user_id", request.user_id).execute()
        return {"success": True, "message": f"Đã trang bị {item_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))