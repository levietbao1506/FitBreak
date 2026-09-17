from pydantic import BaseModel
from typing import Dict, Any
from typing import Optional

class FoodSuggestResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None