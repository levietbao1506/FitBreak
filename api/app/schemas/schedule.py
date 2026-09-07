from pydantic import BaseModel

class schedule(BaseModel):
    timetable : dict
    level_of_physical_activity: int
    aim : int