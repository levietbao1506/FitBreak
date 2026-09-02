from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.database import supabase
#auto_error=False
security = HTTPBearer(auto_error=False) # schema handles extracting & validating authorization

# doi tu cookies sang http reader
# async def auth_middleware(request: Request, call_next):
#     try:
#         token = request.cookies.get("access_token")
#         if token and token.startswith("Bearer "):
#             token = token.split(" ")[1]
#             request.headers.__dict__["_list"].append(
#                 (b"authorization", f"Bearer {token}".encode())
#             )
#         response = await call_next(request)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = str(e))

# xac thuc ng dung hop le 
def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = None
    if credentials:
        token = credentials.credentials
    elif "access_token" in request.cookies:
        raw_cookie = request.cookies["access_token"]
        token = raw_cookie.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Thiếu token xác thực"
        )
    
    try:
        # payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud" : False})
        # user_id = payload.get("sub")
        # if user_id is None:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Xác thực thất bại")
        # return payload
        # ---------------------
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token không hợp lệ hoặc đã bị vô hiệu hóa"
            )
        return {
            "user" : user_response.user.model_dump(),
            "token" : token
        }
    # except jwt.ExpiredSignatureError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    # except jwt.InvalidSignatureError:
    #     raise HTTPException(status_code=401, detail="Invalid token signature. Clear local storage and re-login.")
    except Exception as e:
        # Printing the exact exception to server logs
        # print("Auth Exception:", str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate user: {str(e)}")