from pydantic import BaseModel, Field

class createProfile(BaseModel):
    name : str
    age : int = Field(..., gt=0)
    gender : bool
    height : int = Field(..., gt=0)
    weight : int = Field(..., gt=0)
    goal : str
    activity_frequency : int