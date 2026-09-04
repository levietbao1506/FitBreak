from pydantic import BaseModel
from typing import Optional

class FoodSuggestResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None