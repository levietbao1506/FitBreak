from fastapi import APIRouter, Request, Response, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.database import supabase
from supabase import create_client, ClientOptions
from app.core.database import SUPABASE_URL, SUPABASE_KEY
from app.schemas.createProfile import createProfile
from app.schemas.updateProfile import updateProfile
from app.core.auth import get_current_user
from app.core.calculate_user_stats import calculateBMI, calculateBMR, calculateTDEE
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

@router.post("/profiles/create-profile")
async def createProfile(request: Request, data: createProfile,
                        token: tokenAuthorization = Depends(token_authorization)):
    try:
        bmi =  calculateBMI(data.weight, data.height)
        bmr = calculateBMR(data.weight, data.height, data.age, data.gender)
        tdee = calculateTDEE(bmr, data.activity_frequency)
        token.client.table("profiles").insert({
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
            "tdee" : tdee
        }).execute()
        token.client.table("stats").insert({
            "id" : token.user_id,
            "damage" : 1,
            "coins" : 0
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

        token.client.table("profiles").update({
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
            "tdee" : tdee
        }).eq("id", token.user_id).execute()
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