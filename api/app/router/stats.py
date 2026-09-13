from fastapi import APIRouter, Depends, HTTPException, status
from app.core.token_authorization import tokenAuthorization, token_authorization

router = APIRouter()

@router.get("/get-stats")
async def getStats(token: tokenAuthorization = Depends(token_authorization)):
    try:
        response = token.client.table("stats").select("*").eq("user_id", token.user_id).single().execute()
        stat = response.data
        
        if not stat:
            raise HTTPException(status_code=404, detail="Stats record not found")

        return stat
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))