"""
FastAPI application – FitBreak Food Suggestion API & Backend Services
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Core & Services imports with fallback for both import styles
try:
    from app.core.exceptions import (
        AIModelOfflineException,
        InvalidResponseError,
        InvalidUserInformationError,
        ModelNotFoundError,
        NoMatchingFoodsError,
        RequestTimeoutError,
    )
    from app.core.ollama_client import chat as check_ollama
    from app.core.rate_limiter import RateLimitMiddleware, RateLimiter
    from app.router import auth_route, exercise, profile
    from app.services.rag_service import process_rag_pipeline
except ImportError:
    from api.app.core.exceptions import (
        AIModelOfflineException,
        InvalidResponseError,
        InvalidUserInformationError,
        ModelNotFoundError,
        NoMatchingFoodsError,
        RequestTimeoutError,
    )
    from api.app.core.ollama_client import chat as check_ollama
    from api.app.core.rate_limiter import RateLimitMiddleware, RateLimiter
    from api.app.router import auth_route, exercise, profile
    from api.app.services.rag_service import process_rag_pipeline


# ── Lifespan: kiểm tra kết nối Ollama khi start ──
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

# ── Rate Limiting: Middleware toàn cục (100 req / phút / IP) ──
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# ── CORS: cho phép frontend gọi từ localhost (Vite: 5173, live-server: 5500,...) ──
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


# ── Endpoint gợi ý món ăn (RAG + LLM) có Rate Limit nghiêm ngặt (5 lần / phút) ──
@app.post(
    "/api/food-suggest",
    response_model=FoodSuggestResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60, scope="food-suggest"))],
)
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


# ── Include các Sub-routers ──
app.include_router(auth_route.router, tags=["Auth Routers"])
app.include_router(profile.router, tags=["Create Profile Routers"])
app.include_router(exercise.router, tags=["Exercise"])


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
