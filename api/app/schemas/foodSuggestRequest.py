from pydantic import BaseModel, Field
from typing import Optional

class FoodSuggestRequest(BaseModel):
    calories_need: int = Field(..., ge=800, le=5000, description="Mục tiêu calo/ngày")
    protein_need: int = Field(..., ge=20, le=400, description="Mục tiêu protein (g)")
    daily_budget: int = Field(..., ge=10000, description="Ngân sách VNĐ/ngày")
    aim: str = Field(..., description="Mục tiêu: Tăng cơ / Giảm cân / Cân bằng")
    diet_type: str = Field(..., description="Chế độ ăn: vegetarian / eatclean / home_cooked")
    allergen: Optional[str] = Field("", description="Dị ứng, phân cách bằng ;")