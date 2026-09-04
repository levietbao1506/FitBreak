from fastapi import APIRouter, Depends, HTTPException
from app.schemas.foodSuggestResponse import FoodSuggestResponse
from app.schemas.foodSuggestRequest import FoodSuggestRequest
from app.core.rate_limiter import RateLimiter
from app.services.rag_service import process_rag_pipeline
from app.core.exceptions import (
        AIModelOfflineException,
        InvalidResponseError,
        InvalidUserInformationError,
        ModelNotFoundError,
        NoMatchingFoodsError,
        RequestTimeoutError,
    )

router = APIRouter()

@router.post(
    "/food-suggest",
    response_model=FoodSuggestResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60, scope="food-suggest"))],
)
async def food_suggest(req: FoodSuggestRequest):
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