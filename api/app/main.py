from fastapi import FastAPI
# from app.core.auth import auth_middleware
from app.router import profile, auth_route, exercise
app = FastAPI()

# app.middleware("http")(auth_middleware)

app.include_router(auth_route.router, tags=["Auth Routers"])
app.include_router(profile.router, tags=["Create Profile Routers"])
app.include_router(exercise.router, tags=["Exercise"])

@app.get("/")
async def home():
    return {"message" : "Dang Nhap Thanh Cong"}
