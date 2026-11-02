from fastapi import APIRouter, Request, Response, Form, Depends, HTTPException, status
from app.schemas.createProfile import createProfile
from app.schemas.updateProfile import updateProfile
from app.schemas.medicalCheckup import MedicalCheckupRequest
from app.services.medical_checkup import medical_checkup
from app.core.calculate_user_stats import calculateBMI, calculateBMR, calculateTDEE, calculateProtein
from app.core.token_authorization import tokenAuthorization, token_authorization


def _generate_diet_recommendation_from_bmi(weight: float, height: float) -> str:
    if not weight or not height or height <= 0:
        return None
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        return "Thể trạng nhẹ cân: Cần bổ sung thêm calo thặng dư giàu dinh dưỡng (các loại hạt, quả bơ, thực phẩm giàu đạm) để hỗ trợ tăng cân và tăng cơ an toàn."
    elif bmi >= 25.0:
        return "Thể trạng thừa cân / béo phì: Ưu tiên thực đơn giảm thâm hụt calo nhẹ, tăng tỷ trọng protein nạc và rau xanh nhiều chất xơ, hạn chế đồ chiên xào nhiều dầu mỡ."
    elif bmi >= 23.0:
        return "Thể trạng tiền béo phì: Cần kiểm soát lượng tinh bột tinh chế và dầu mỡ, ưu tiên protein nạc và rau củ để duy trì vóc dáng săn chắc."
    return "Thể trạng cân đối: Duy trì chế độ ăn đa dạng dưỡng chất, phân bổ đều đặn Protein, Carb phức hợp và chất béo lành mạnh."

router = APIRouter()

@router.post("/profiles/create-profile")
async def createProfile(request: Request, data: createProfile,
                        token: tokenAuthorization = Depends(token_authorization)):
    try:
        bmi = calculateBMI(data.weight, data.height)
        bmr = calculateBMR(data.weight, data.height, data.age, data.gender)
        tdee = calculateTDEE(bmr, data.activity_frequency)
        protein = calculateProtein(data.weight, data.activity_frequency)
        food_rec = _generate_diet_recommendation_from_bmi(data.weight, data.height)

        token.client.table("profiles").insert({
            "id": token.user_id,
            "email": token.user_email,
            "name": data.name,
            "age": data.age,
            "gender": data.gender,
            "height": data.height,
            "weight": data.weight,
            "goal": data.goal,
            "activity_frequency": data.activity_frequency,
            "bmi": bmi,
            "bmr": bmr,
            "tdee": tdee,
            "protein": protein,
            "food_recommendation": food_rec
        }).execute()

        team_response = token.client.table("stats").select("team").order("team", desc=True).limit(1).execute()
        if team_response.data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khong tim thay data")
        
        max_current_team = team_response.data[0]['team'] if team_response.data else 0
        max_new_team = max_current_team + 1

        token.client.table("stats").insert({
            "user_id": token.user_id,
            "team": max_new_team,
            "email": token.user_email,
            "damage": 1,
            "coins": 0
        }).execute()

        # dang su dung mock data
        boss_response = token.client.table("boss").select("*").eq("id", 1).single().execute()
        boss_stat = boss_response.data
        if not boss_stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boss not exist")

        token.client.table("raid").insert({
            "team": max_new_team,
            "boss_id": boss_stat["id"],
            "boss_name": boss_stat["name"],
            "health": boss_stat["health"],
            "reward_coins": boss_stat["reward_coins"]
        }).execute()

        token.client.table("user").insert({
            "user_id": token.user_id,
            "skin": "Orange Skin",
            "shirt": "Blue Shirt",
            "hair": "Black Hair",
            "background": None,
            "weapon": None
        }).execute()

        return {"message": "Tạo profile thành công"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/profiles/update-profile")
async def updateProfile(request: Request, data: updateProfile,
                        token: tokenAuthorization = Depends(token_authorization)):
    try:
        bmi = calculateBMI(data.weight, data.height)
        bmr = calculateBMR(data.weight, data.height, data.age, data.gender)
        tdee = calculateTDEE(bmr, data.activity_frequency)
        protein = calculateProtein(data.weight, data.activity_frequency)

        update_payload = {
            "id" : token.user_id,
            "email" : token.user_email,
            "name" : data.name,
            "age" : data.age,
            "gender" : data.gender,
            "height" : data.height,
            "weight" : data.weight,
            "goal" : data.goal,
            "activity_frequency" : data.activity_frequency,
            "bmi" : bmi,
            "bmr" : bmr,
            "tdee" : tdee,
            "protein": protein
        }

        # Kiểm tra xem hồ sơ đã có food_recommendation từ medical checkup chưa, nếu chưa thì cập nhật theo BMI mới
        current_prof = token.client.table("profiles").select("food_recommendation").eq("id", token.user_id).execute()
        has_existing_rec = current_prof.data and current_prof.data[0].get("food_recommendation")
        if not has_existing_rec:
            update_payload["food_recommendation"] = _generate_diet_recommendation_from_bmi(data.weight, data.height)

        token.client.table("profiles").update(update_payload).eq("id", token.user_id).execute()
        return {"message": "Cập nhật profile thành công"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/profiles/get-profile-by-email/{email}")
async def getProfileByEmail(email: str, token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("profiles").select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        return None

@router.post("/profiles/medical-checkup")
async def analyze_medical_checkup(data: MedicalCheckupRequest, token: tokenAuthorization = Depends(token_authorization)):
    try:
        # Neu weight va height khong duoc gui len tu form y te, lay tu profile
        w = data.weight
        h = data.height
        if w is None or h is None:
            user_prof = token.client.table("profiles").select("weight, height").eq("id", token.user_id).execute()
            if user_prof.data and len(user_prof.data) > 0:
                p = user_prof.data[0]
                if w is None and p.get("weight"):
                    w = float(p["weight"])
                if h is None and p.get("height"):
                    h = float(p["height"])

        result = await medical_checkup(
            weight=w,
            height=h,
            sys=data.sys,
            dia=data.dia,
            time=data.time,
            glycemic_index=data.glycemic_index,
            spo2_index=data.spo2_index
        )

        # Lấy danh sách lời khuyên dinh dưỡng từ kết quả khám sức khỏe
        diet_advices = result.get("recommendations", {}).get("diet_advice", [])
        if diet_advices:
            joined_advice = "; ".join(diet_advices)
            try:
                token.client.table("profiles").update({
                    "food_recommendation": joined_advice
                }).eq("id", token.user_id).execute()
            except Exception as save_err:
                print(f"[WARN] Không thể cập nhật food_recommendation vào profiles: {save_err}")

        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
