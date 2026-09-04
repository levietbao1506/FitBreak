from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from app.core.calculate_user_stats import calculateBMI, calculateBMR, calculateTDEE
    from app.core.token_authorization import tokenAuthorization, token_authorization
    from app.schemas.createProfile import createProfile
    from app.schemas.updateProfile import updateProfile
except ImportError:
    from api.app.core.calculate_user_stats import calculateBMI, calculateBMR, calculateTDEE
    from api.app.core.token_authorization import tokenAuthorization, token_authorization
    from api.app.schemas.createProfile import createProfile
    from api.app.schemas.updateProfile import updateProfile

router = APIRouter()


@router.post("/profiles/create-profile")
async def create_profile(
    request: Request,
    data: createProfile,
    token: tokenAuthorization = Depends(token_authorization),
):
    try:
        bmi = calculateBMI(data.weight, data.height)
        bmr = calculateBMR(data.weight, data.height, data.age, data.gender)
        tdee = calculateTDEE(bmr, data.activity_frequency)

        profile_payload = {
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
        }

        token.client.table("profiles").insert(profile_payload).execute()
        token.client.table("stats").insert({
            "id": token.user_id,
            "damage": 1,
            "coins": 0,
        }).execute()

        return {
            "success": True,
            "message": "Tạo hồ sơ thành công",
            "data": profile_payload,
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/profiles/update-profile")
async def update_profile(
    request: Request,
    data: updateProfile,
    token: tokenAuthorization = Depends(token_authorization),
):
    try:
        bmi = calculateBMI(data.weight, data.height)
        bmr = calculateBMR(data.weight, data.height, data.age, data.gender)
        tdee = calculateTDEE(bmr, data.activity_frequency)

        update_payload = {
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
        }

        token.client.table("profiles").update(update_payload).eq("id", token.user_id).execute()

        return {
            "success": True,
            "message": "Cập nhật thông tin thành công",
            "data": update_payload,
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))