from pydantic import BaseModel

class logIn(BaseModel):
    email : str
    password : str