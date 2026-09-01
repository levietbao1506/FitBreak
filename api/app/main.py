from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import profile, auth_route, exercise

app = FastAPI()

origins = [
    "http://localhost:5173" # doi dua tren local host cua frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(auth_route.router, tags=["Auth Routers"])
app.include_router(profile.router, tags=["Create Profile Routers"])
app.include_router(exercise.router, tags=["Exercise"])

@app.get("/")
async def home():
    return {"message" : "Dang Nhap Thanh Cong"}
