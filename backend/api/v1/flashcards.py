from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from core.dependencies import get_db
from models.flashcard import Flashcard
from models.deck import Deck
from schemas.flashcard import FlashcardResponse

router = APIRouter(prefix="/decks", tags=["Flashcards"])

@router.get("/{deck_id}/cards/due", response_model=List[FlashcardResponse])
def get_due_cards(deck_id: int, db: Session = Depends(get_db)):
    # Kiểm tra deck tồn tại
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    now = datetime.utcnow()

    due_cards = db.query(Flashcard).filter(
        Flashcard.deck_id == deck_id,
        Flashcard.next_review <= now
    ).all()

    return due_cards

@router.put("/cards/{card_id}", response_model=FlashcardResponse)
def update_flashcard_back_text(card_id: int, back_text: str, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card.back_text = back_text
    db.commit()
    db.refresh(card)
    return card