from fastapi import APIRouter, Request, Response, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.database import supabase
from app.schemas.signUp import signUp
from app.schemas.logIn import logIn
from app.schemas.authResponse import authResponse

router = APIRouter()

@router.get("/register")
async def registerForm(request: Request):
    return {"message" : "success"}

@router.post("/register")
async def register(data: signUp):
    try:
        auth_response = supabase.auth.sign_up({
            "email" : data.email,
            "password" : data.password
        })
        if auth_response is None:
            # raise loi
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Register that bai")
        return authResponse(
            success = True,
            message = "Đăng ký thành công",
            access_token = auth_response.session.access_token,
            user = auth_response.user
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/login")
async def logInForm(request: Request):
    return {"message" : "success"}

@router.post("/login")
async def logIn(response: Response, data: logIn):
    # response dung de ghi cookie cho cac lan dang nhap sau
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email" : data.email,
            "password" : data.password
        })
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác"
            )
        access_token = auth_response.session.access_token
        # response = RedirectResponse("/", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True,
                            path="/", samesite="lax", secure=False)
        return authResponse(
            success = True,
            message = "Login successful",
            access_token = access_token,
            user = auth_response.user
        )
    except Exception as e:
        # raise loi
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

@router.get("/logout")
async def logOut(response: Response):
    response.delete_cookie(key="access_token")
    return authResponse(
        success = True,
        message = "Đăng xuất thành công",
        access_token = None,
        user = None
    )