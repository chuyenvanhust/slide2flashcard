from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class FlashcardBase(BaseModel):
    image_path: str
    back_text: Optional[str] = None
    card_type: str
    source_page: int
    confidence: Optional[float] = None

class FlashcardCreate(FlashcardBase):
    deck_id: int

# Schema phục vụ riêng cho endpoint PUT /cards/{id} để sửa text mặt sau
class FlashcardUpdate(BaseModel):
    back_text: str

class FlashcardResponse(FlashcardBase):
    id: int
    deck_id: int
    created_at: datetime

    class Config:
        from_attributes = True