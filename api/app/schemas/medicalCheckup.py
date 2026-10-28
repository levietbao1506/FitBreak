from pydantic import BaseModel, Field
from typing import Optional

class MedicalCheckupRequest(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    sys: Optional[int] = None
    dia: Optional[int] = None
    time: Optional[int] = Field(None, description="0: Lúc đói (ít nhất 8 tiếng), 1: Trước bữa ăn, 2: Ngẫu nhiên trong ngày")
    glycemic_index: Optional[int] = None
    spo2_index: Optional[int] = None

