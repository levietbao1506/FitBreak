from fastapi import APIRouter, Request, Response, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.database import supabase

router = APIRouter()

@router.get("/register")
async def registerForm(request: Request):
    return {"message" : "success"}

@router.post("/register")
async def register(email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_up({
            "email" : email,
            "password" : password
        })
        if auth_response is None:
            # raise loi
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Register that bai")
        return {"success" : True}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/login")
async def logInForm(request: Request):
    return {"message" : "success"}

@router.post("/login")
async def logIn(response: Response, email: str = Form(...), password: str = Form(...)):
    # response dung de ghi cookie cho cac lan dang nhap sau
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email" : email,
            "password" : password
        })
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác"
            )
        access_token = auth_response.session.access_token
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True,
                            path="/", samesite="lax", secure=False)
        return response
    except Exception as e:
        # raise loi
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

@router.get("/logout")
async def logOut(response: Response):
    response = RedirectResponse("/sign-in", status_code=303) # chinh status code
    response.delete_cookie(key="access_token")
    return response