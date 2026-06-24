from datetime import datetime
from pydantic import BaseModel
from typing import Literal

# Dữ liệu từ Frontend gửi lên khi bấm nút đánh giá thẻ
class ReviewCreate(BaseModel):
    rating: Literal["easy", "medium", "hard", "again"]

class ReviewResponse(BaseModel):
    id: int
    card_id: int
    rating: str
    reviewed_at: datetime
    next_review: datetime
    interval: int
    ease_factor: float

    class Config:
        from_attributes = True