from fastapi import APIRouter
from app.core.purchaseFunction import purchase_item
from app.schemas.purchase import PurchaseRequest

router = APIRouter()

@router.post("/purchase")
async def purchase(request: PurchaseRequest):
    result = await purchase_item(
        request.user_id,
        request.item_id
    )

    return result