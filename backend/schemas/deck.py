from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Optional

class DeckBase(BaseModel):
    name: str

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    name: str

class DeckResponse(DeckBase):
    id: int
    total_cards: int
    known_cards: int = 0
    due_cards: int = 0
    card_types: Dict[str, int] = {}
    created_at: datetime

    class Config:
        from_attributes = True  # Thay thế cho orm_mode=True ở Pydantic v1

class TransferRequest(BaseModel):
    card_ids: list[int]
    target_deck_id: Optional[int] = None
    target_deck_name: Optional[str] = None
    action: str # "copy" or "move"