from pydantic import BaseModel

class signUp(BaseModel):
    email : str
    password : str