from pydantic import BaseModel, Field

class updateProfile(BaseModel):
    name : str
    age : int = Field(..., gt=0)
    gender : bool
    height : int
    weight : int
    goal : str
    activity_frequency : int
    