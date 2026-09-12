from fastapi import HTTPException, Depends
from dataclasses import dataclass
from supabase import create_client, Client
from app.core.database import SUPABASE_URL, SUPABASE_KEY
from app.core.auth import get_current_user

@dataclass
class tokenAuthorization:
    client: Client
    user_id: str
    user_email: str


def token_authorization(
    current_user: dict = Depends(get_current_user)
) -> tokenAuthorization:
    user = current_user.get("user")
    token = current_user.get("token")

    user_email = user.get("email")
    user_id = user.get("id")

    if not user_email or not user_id:
        raise HTTPException(status_code=401, detail="Email not found in token")

    user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_supabase.postgrest.auth(token)

    return tokenAuthorization(
        client = user_supabase,
        user_id = user_id,
        user_email = user_email
    )