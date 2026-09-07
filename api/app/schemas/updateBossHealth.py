from pydantic import BaseModel

class updateBossHealth(BaseModel):
    team : int
    damage : int