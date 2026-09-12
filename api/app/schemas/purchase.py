from pydantic import BaseModel

class PurchaseRequest(BaseModel):
      user_id: int
      item_id: int