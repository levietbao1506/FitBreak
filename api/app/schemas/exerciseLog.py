from pydantic import BaseModel
from datetime import datetime

class exerciseLog(BaseModel):
    exercise_id: str
    completed_at: datetime
    reward_coins: int