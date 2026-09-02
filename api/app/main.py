"""
FastAPI application – FitBreak Food Suggestion API
Endpoint: POST /api/food-suggest
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from api.app.services.rag_service import process_rag_pipeline
from api.app.core.ollama_client import chat as check_ollama
from api.app.core.exceptions import (
    AIModelOfflineException,
    InvalidResponseError,
    InvalidUserInformationError,
    ModelNotFoundError,
    NoMatchingFoodsError,
    RequestTimeoutError,
)


# ── Lifespan: kiểm tra kết nối Ollama khi start ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await check_ollama()
        print("[OK] Ollama connection OK")
    except AIModelOfflineException as e:
        print(f"[WARN] Ollama chua san sang: {e}")
    yield


app = FastAPI(
    title="FitBreak API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS: cho phép frontend gọi từ localhost hoặc file:// ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schema ──
class FoodSuggestRequest(BaseModel):
    calories_need: int = Field(..., ge=800, le=5000, description="Mục tiêu calo/ngày")
    protein_need: int = Field(..., ge=20, le=400, description="Mục tiêu protein (g)")
    daily_budget: int = Field(..., ge=10000, description="Ngân sách VNĐ/ngày")
    aim: str = Field(..., description="Mục tiêu: Tăng cơ / Giảm cân / Cân bằng")
    diet_type: str = Field(..., description="Chế độ ăn: vegetarian / eatclean / home_cooked")
    allergen: Optional[str] = Field("", description="Dị ứng, phân cách bằng ;")


class FoodSuggestResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


# ── Endpoint chính ──
@app.post("/api/food-suggest", response_model=FoodSuggestResponse)
async def food_suggest(req: FoodSuggestRequest):
    """Gọi RAG pipeline để gợi ý thực đơn 3 bữa dựa trên thông tin người dùng."""
    try:
        user_info = req.model_dump()
        result = await process_rag_pipeline(user_info)
        return FoodSuggestResponse(success=True, result=result)

    except AIModelOfflineException as e:
        raise HTTPException(status_code=503, detail=f"Ollama offline: {e}")
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidUserInformationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except NoMatchingFoodsError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RequestTimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except InvalidResponseError as e:
        raise HTTPException(status_code=502, detail=f"LLM trả về không hợp lệ: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {e}")


# ── Health check ──
@app.get("/api/health")
async def health_check():
    try:
        await check_ollama()
        return {"status": "ok", "ollama": "connected"}
    except Exception as e:
        return {"status": "degraded", "ollama": str(e)}


# ── Root endpoint ──
@app.get("/")
async def root():
    return {"message": "Welcome to FitBreak API! Go to /docs for API documentation."}

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
