from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from supabase import Client, create_client

try:
    from app.core.auth import get_current_user
    from app.core.database import SUPABASE_KEY, SUPABASE_URL
except ImportError:
    from api.app.core.auth import get_current_user
    from api.app.core.database import SUPABASE_KEY, SUPABASE_URL


@dataclass
class tokenAuthorization:
    client: Client
    user_id: str
    user_email: str


# Alias for PEP-8 naming compatibility
TokenAuthorization = tokenAuthorization


def token_authorization(
    current_user: dict = Depends(get_current_user),
) -> tokenAuthorization:
    user = current_user.get("user")
    token = current_user.get("token")

    if not user or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin người dùng hoặc token không hợp lệ",
        )

    user_email = user.get("email")
    user_id = user.get("id")

    if not user_email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy thông tin email hoặc user_id trong token",
        )

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cơ sở dữ liệu Supabase chưa được cấu hình",
        )

    user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_supabase.postgrest.auth(token)

    return tokenAuthorization(
        client=user_supabase,
        user_id=user_id,
        user_email=user_email,
    )