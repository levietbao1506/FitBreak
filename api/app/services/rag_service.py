import json
from pathlib import Path
import re
from typing import Optional
import unicodedata
import pandas as pd
from pydantic import BaseModel, Field

try:
    from app.core.exceptions import (
        InvalidResponseError,
        InvalidUserInformationError,
        NoMatchingFoodsError,
    )
    from app.core.ollama_client import generate_chat
    from app.services.prompt_builder import prompt_builder
except ImportError:
    from api.app.core.exceptions import (
        InvalidResponseError,
        InvalidUserInformationError,
        NoMatchingFoodsError,
    )
    from api.app.core.ollama_client import generate_chat
    from api.app.services.prompt_builder import prompt_builder

# DATABASE #
DATA_PATH = Path(__file__).resolve().parents[1] / "core" / "database" / "Vietnamese_Food_Database.csv"
DF_FOODS = pd.read_csv(DATA_PATH)
DF_FOODS["allergens"] = DF_FOODS["allergens"].fillna("")

# Dùng cơm trắng 100g làm chuẩn tính toán calo/protein/carbs/fat/giá
RICE_NUTRIENTS_PER_100G = {"calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3, "price": 2000}


def get_user_value(user_information: dict, field: str, default=None):
    if isinstance(user_information, dict):
        return user_information.get(field, default)
    return getattr(user_information, field, default)


def filter_foods(df: pd.DataFrame, user_diet: str, user_allergens) -> pd.DataFrame:
    if isinstance(user_allergens, str):
        user_allergens = [
            a.strip().lower() for a in user_allergens.replace(",", ";").split(";") if a.strip()
        ]
    else:
        user_allergens = [
            a.strip().lower() for a in (user_allergens or []) if a and a.strip()
        ]

    def has_allergen(item_allergens):
        if not item_allergens:
            return False
        item_list = [a.strip().lower() for a in str(item_allergens).split(";")]
        return any(a in user_allergens for a in item_list)

    # 1. Lọc dị ứng
    valid_df = df[~df["allergens"].apply(has_allergen)].copy()

    # 2. Lọc chế độ ăn (chuẩn hóa loại bỏ gạch dưới để khớp cả eatclean lẫn eat_clean)
    def clean_diet_tag(tag: str) -> str:
        return str(tag).replace("_", "").replace("-", "").strip().lower()

    if user_diet:
        target_diet = clean_diet_tag(user_diet)
        valid_df = valid_df[
            valid_df["diet_type"].apply(
                lambda diets: target_diet in {clean_diet_tag(d) for d in str(diets).split(";")}
            )
        ]

    return valid_df


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", str(text).strip().lower())


def get_dish_info(dish_name: str, df: pd.DataFrame) -> dict:
    """Helper tra cứu thông tin dinh dưỡng an toàn từ tên món."""
    norm_target = normalize_text(dish_name)

    # 1. Khớp chính xác 100% (sau khi chuẩn hóa Unicode & lowercase)
    matched = df[df["name"].apply(normalize_text) == norm_target]

    # 2. Nếu không khớp chính xác, thử tìm kiếm chuỗi con (fallback)
    if matched.empty:
        matched = df[df["name"].apply(normalize_text).str.contains(norm_target, regex=False)]

    # 3. Nếu vẫn không có, lấy món đầu tiên của danh sách để tránh crash (chống hallucination)
    if matched.empty and not df.empty:
        matched = df.head(1)

    if not matched.empty:
        row = matched.iloc[0]
        ingredients_val = row.get("ingredients", row["name"])
        return {
            "calories": float(row.get("calories", 0)),
            "protein": float(row.get("protein_g", 0)),
            "carbs": float(row.get("carbs_g", 0)),
            "fat": float(row.get("fat_g", 0)),
            "price": float(row.get("cost_vnd", 0)),
            "ingredients": str(ingredients_val) if pd.notna(ingredients_val) else row["name"],
            "real_name": row["name"],
        }
    raise InvalidResponseError(f"Món ăn không có trong database: {dish_name}")


# PARSE DISH #
class Breakfast(BaseModel):
    dish_name: str


class MainMeal(BaseModel):
    main_dish: str
    rice_grams: int = Field(default=0, ge=0, le=300, description="Số gram cơm (tối đa 300g)")


class MealsPlan(BaseModel):
    breakfast: Breakfast
    lunch: MainMeal
    dinner: MainMeal


class LLMMealResponse(BaseModel):
    estimated_total_cost: Optional[float] = 0
    meals: MealsPlan


def parse_llm_meal_response(raw_text: str) -> LLMMealResponse:
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        raise InvalidResponseError("LLM không trả về JSON hợp lệ")
    json_str = match.group(0)
    # Loại bỏ trailing commas thường gặp khi LLM sinh JSON
    cleaned_json = re.sub(r",\s*([\]}])", r"\1", json_str)
    try:
        data = json.loads(cleaned_json)
        return LLMMealResponse(**data)
    except Exception as e:
        raise InvalidResponseError(f"Không thể parse JSON từ LLM: {str(e)}")


def validate_user_information(user_information: dict) -> None:
    required_fields = ("calories_need", "daily_budget", "protein_need", "aim", "diet_type")
    missing_fields = [
        field for field in required_fields if get_user_value(user_information, field) is None
    ]
    if missing_fields:
        raise InvalidUserInformationError(
            f"Thiếu thông tin người dùng: {', '.join(missing_fields)}"
        )

    numeric_fields = ("calories_need", "daily_budget", "protein_need")
    for field in numeric_fields:
        value = get_user_value(user_information, field)
        if not isinstance(value, (int, float)) or value < 0:
            raise InvalidUserInformationError(f"{field} phải là số không âm")


def is_carb_heavy_dish(dish_name: str) -> bool:
    name_lower = str(dish_name).lower()
    carb_keywords = [
        "bún", "phở", "mì", "miến", "hủ tiếu", "bánh mì",
        "cơm tấm", "cơm chiên", "cơm gà", "cháo", "bánh cuốn", "bánh canh", "xôi"
    ]
    return any(kw in name_lower for kw in carb_keywords)


def generate_meal_data(response: str, df_pool: pd.DataFrame, user_information: dict) -> dict:
    meal_plan = parse_llm_meal_response(response)

    # 1. Bữa sáng
    bf_name_llm = meal_plan.meals.breakfast.dish_name
    bf_info = get_dish_info(bf_name_llm, df_pool)
    used_names = {bf_info["real_name"].lower()}

    # 2. Bữa trưa (chống trùng với bữa sáng)
    lu = meal_plan.meals.lunch
    lu_main = get_dish_info(lu.main_dish, df_pool)
    if lu_main["real_name"].lower() in used_names:
        fallback_lunch = df_pool[~df_pool["name"].str.lower().isin(used_names)]
        if not fallback_lunch.empty:
            lu_main = get_dish_info(fallback_lunch.iloc[0]["name"], df_pool)
    used_names.add(lu_main["real_name"].lower())

    # Quy tắc cơm: món đã có sẵn tinh bột thì rice_grams = 0
    lu_rice_grams = 0 if is_carb_heavy_dish(lu_main["real_name"]) else lu.rice_grams

    lu_rice_cal = (lu_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
    lu_rice_pro = (lu_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
    lu_rice_carb = (lu_rice_grams / 100) * RICE_NUTRIENTS_PER_100G.get("carbs", 28.0)
    lu_rice_fat = (lu_rice_grams / 100) * RICE_NUTRIENTS_PER_100G.get("fat", 0.3)
    lu_rice_cost = (lu_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]

    lu_total_cal = lu_main["calories"] + lu_rice_cal
    lu_total_pro = lu_main["protein"] + lu_rice_pro
    lu_total_carb = lu_main["carbs"] + lu_rice_carb
    lu_total_fat = lu_main["fat"] + lu_rice_fat
    lu_total_cost = lu_main["price"] + lu_rice_cost

    # 3. Bữa tối (chống trùng với bữa sáng và trưa)
    dn = meal_plan.meals.dinner
    dn_main = get_dish_info(dn.main_dish, df_pool)
    if dn_main["real_name"].lower() in used_names:
        fallback_dinner = df_pool[~df_pool["name"].str.lower().isin(used_names)]
        if not fallback_dinner.empty:
            dn_main = get_dish_info(fallback_dinner.iloc[0]["name"], df_pool)

    dn_rice_grams = 0 if is_carb_heavy_dish(dn_main["real_name"]) else dn.rice_grams

    dn_rice_cal = (dn_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["calories"]
    dn_rice_pro = (dn_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["protein"]
    dn_rice_carb = (dn_rice_grams / 100) * RICE_NUTRIENTS_PER_100G.get("carbs", 28.0)
    dn_rice_fat = (dn_rice_grams / 100) * RICE_NUTRIENTS_PER_100G.get("fat", 0.3)
    dn_rice_cost = (dn_rice_grams / 100) * RICE_NUTRIENTS_PER_100G["price"]

    dn_total_cal = dn_main["calories"] + dn_rice_cal
    dn_total_pro = dn_main["protein"] + dn_rice_pro
    dn_total_carb = dn_main["carbs"] + dn_rice_carb
    dn_total_fat = dn_main["fat"] + dn_rice_fat
    dn_total_cost = dn_main["price"] + dn_rice_cost

    # Tổng kết
    total_cal = bf_info["calories"] + lu_total_cal + dn_total_cal
    total_pro = bf_info["protein"] + lu_total_pro + dn_total_pro
    total_carb = bf_info["carbs"] + lu_total_carb + dn_total_carb
    total_fat = bf_info["fat"] + lu_total_fat + dn_total_fat
    total_cost = bf_info["price"] + lu_total_cost + dn_total_cost

    target_cal = get_user_value(user_information, "calories_need")
    target_pro = get_user_value(user_information, "protein_need")
    budget = get_user_value(user_information, "daily_budget")

    # Tên món hiển thị (chỉ kèm cơm nếu có ăn thêm cơm)
    lu_display = f"{lu_main['real_name']} + {lu_rice_grams}g cơm" if lu_rice_grams > 0 else lu_main["real_name"]
    dn_display = f"{dn_main['real_name']} + {dn_rice_grams}g cơm" if dn_rice_grams > 0 else dn_main["real_name"]

    summary_text = (
        f"Bữa sáng: {bf_info['real_name']} ({bf_info['calories']:.0f} kcal / {bf_info['protein']:.1f}g protein / {bf_info['price']:,.0f}đ)\n"
        f"Nguyên liệu: {bf_info['ingredients']}\n\n"
        f"Bữa trưa: {lu_display} ({lu_total_cal:.0f} kcal / {lu_total_pro:.1f}g protein / {lu_total_cost:,.0f}đ)\n"
        f"Nguyên liệu: {lu_main['ingredients']}\n\n"
        f"Bữa tối: {dn_display} ({dn_total_cal:.0f} kcal / {dn_total_pro:.1f}g protein / {dn_total_cost:,.0f}đ)\n"
        f"Nguyên liệu: {dn_main['ingredients']}\n\n"
        f"Tổng kết ngày:\n"
        f"    Tổng Calo: {total_cal:.0f} / {target_cal} kcal\n"
        f"    Tổng Protein: {total_pro:.1f} / {target_pro} g\n"
        f"    Tổng Chi phí: {total_cost:,.0f} / {budget:,.0f} đ"
    )

    structured_plan = {
        "meals": {
            "breakfast": {
                "name": bf_info["real_name"],
                "calories": round(bf_info["calories"]),
                "protein": round(bf_info["protein"], 1),
                "carbs": round(bf_info["carbs"], 1),
                "fat": round(bf_info["fat"], 1),
                "cost": round(bf_info["price"]),
                "ingredients": bf_info["ingredients"],
                "rice_grams": 0,
            },
            "lunch": {
                "name": lu_display,
                "calories": round(lu_total_cal),
                "protein": round(lu_total_pro, 1),
                "carbs": round(lu_total_carb, 1),
                "fat": round(lu_total_fat, 1),
                "cost": round(lu_total_cost),
                "ingredients": lu_main["ingredients"],
                "rice_grams": lu.rice_grams,
            },
            "dinner": {
                "name": dn_display,
                "calories": round(dn_total_cal),
                "protein": round(dn_total_pro, 1),
                "carbs": round(dn_total_carb, 1),
                "fat": round(dn_total_fat, 1),
                "cost": round(dn_total_cost),
                "ingredients": dn_main["ingredients"],
                "rice_grams": dn.rice_grams,
            },
        },
        "totals": {
            "calories": round(total_cal),
            "protein": round(total_pro, 1),
            "carbs": round(total_carb, 1),
            "fat": round(total_fat, 1),
            "cost": round(total_cost),
        },
        "is_ai": True,
    }

    return {
        "summary": summary_text,
        "structured_plan": structured_plan,
    }


def format_meal_summary(response: str, df_pool: pd.DataFrame, user_information: dict) -> str:
    """Giữ hàm này để đảm bảo tương thích ngược."""
    data = generate_meal_data(response, df_pool, user_information)
    return data["summary"]


# MAIN RAG #
async def process_rag_pipeline(user_information: dict) -> dict:
    validate_user_information(user_information)

    diet_type = get_user_value(user_information, "diet_type")
    allergen = get_user_value(user_information, "allergen", "")
    exclude_dishes = get_user_value(user_information, "exclude_dishes", [])

    # Retrieval: Lọc danh sách món hợp lệ từ CSV
    filtered_df = filter_foods(DF_FOODS, diet_type, allergen)
    if filtered_df.empty:
        raise NoMatchingFoodsError("Không tìm thấy món ăn phù hợp với chế độ ăn và dị ứng.")

    # Truyền filtered_df vào prompt_builder để LLM chọn món
    prompt = await prompt_builder(
        calories_need=get_user_value(user_information, "calories_need"),
        daily_budget=get_user_value(user_information, "daily_budget"),
        protein_need=get_user_value(user_information, "protein_need"),
        aim=get_user_value(user_information, "aim"),
        diet_type=diet_type,
        allergen=allergen,
        filtered_food=filtered_df,
        exclude_dishes=exclude_dishes,
    )

    response = await generate_chat(prompt, response_format=LLMMealResponse.model_json_schema())
    return generate_meal_data(response, filtered_df, user_information)