from pydantic import BaseModel

class PurchaseRequest(BaseModel):
    user_id: str
    item_id: int