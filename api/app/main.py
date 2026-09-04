from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import (
    AIModelOfflineException
)
from app.core.ollama_client import chat as check_ollama
from app.core.rate_limiter import RateLimitMiddleware
from app.router import auth_route, exercise, profile, foodSuggest
from app.core.ollama_client import chat as check_ollama

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await check_ollama()
        print("[OK] Ollama connection OK")
    except AIModelOfflineException as e:
        print(f"[WARN] Ollama chưa sẵn sàng: {e}")
    except Exception as e:
        print(f"[WARN] Không thể kiểm tra Ollama lúc khởi động: {e}")
    yield


app = FastAPI(
    title="FitBreak API",
    description="FitBreak - Pomodoro Active Break & AI Food Suggestion API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_route.router, tags=["Auth Routers"])
app.include_router(profile.router, tags=["Create Profile Routers"])
app.include_router(exercise.router, tags=["Exercise"])
app.include_router(foodSuggest.router, tags=["Food Suggest"])

@app.get("/api/health")
async def health_check():
    try:
        await check_ollama()
        return {"status": "ok", "ollama": "connected"}
    except Exception as e:
        return {"status": "degraded", "ollama": str(e)}

@app.get("/")
async def root():
    return {"message": "Welcome to FitBreak API! Go to /docs for API documentation."}
