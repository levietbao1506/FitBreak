from pydantic import BaseModel
from typing import Any, Optional

class authResponse(BaseModel):
    success : bool
    message : str
    access_token : Optional[str] = None
    user : Optional[Any] = None