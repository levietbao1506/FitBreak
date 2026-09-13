from database import supabase

def purchase_item(user_id, item_id):
      # Lấy thông tin user
      user_result = supabase \
            .table("users") \
            .select("*") \
            .eq("id", user_id) \
            .single() \
            .execute()

      user = user_result.data

      if user is None:
            return {
                  "success": False,
                  "message": "User không tồn tại"
            }

      # Lấy thông tin item
      item_result = supabase \
            .table("items") \
            .select("*") \
            .eq("id", item_id) \
            .single() \
            .execute()

      item = item_result.data

      if item is None:
            return {
                  "success": False,
                  "message": "Item không tồn tại"
            }

      # Kiểm tra stock
      if item["stock"] <= 0:
            return {
                  "success": False,
                  "message": "Item đã hết hàng"
            }

      # Kiểm tra coin
      if user["coins"] < item["price"]:
            return {
                  "success": False,
                  "message": "Không đủ coin"
            }

      # Tính số coin còn lại
      remaining_coin = user["coins"] - item["price"]

      # Update coin
      supabase \
            .table("users") \
            .update({
                  "coins": remaining_coin
            }) \
            .eq("id", user_id) \
            .execute()

      # Update stock
      remaining_stock = item["stock"] - 1

      supabase \
            .table("items") \
            .update({
                  "stock": remaining_stock
            }) \
            .eq("id", item_id) \
            .execute()

      return {
            "success": True,
            "message": "Mua hàng thành công",
            "remaining_coin": remaining_coin
      }