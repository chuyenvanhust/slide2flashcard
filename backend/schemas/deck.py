from datetime import datetime
from pydantic import BaseModel
from typing import Dict

class DeckBase(BaseModel):
    name: str
    source_file: str

class DeckCreate(DeckBase):
    pass

class DeckResponse(DeckBase):
    id: int
    total_cards: int
    known_cards: int = 0
    due_cards: int = 0
    card_types: Dict[str, int] = {}
    created_at: datetime

    class Config:
        from_attributes = True  # Thay thế cho orm_mode=True ở Pydantic v1