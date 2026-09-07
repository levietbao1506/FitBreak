from fastapi import APIRouter, Depends, HTTPException, status
from app.core.token_authorization import tokenAuthorization, token_authorization
from app.schemas.joinTeam import joinTeam

router = APIRouter()

@router.post("/join-team")
async def joinTeam(data: joinTeam, 
                   token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("stats").select("*").eq("email", data.email).single().execute()
        stat = response.data
        if not stat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not exist")
        team = stat["team"]

        token.client.table("stats").update({
            "team" : team
        }).eq("id", token.user_id).execute()

        return {"message" : "Join team successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
