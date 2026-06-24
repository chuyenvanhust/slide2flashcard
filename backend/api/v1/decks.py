from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from core.dependencies import get_db
from models.deck import Deck
from schemas.deck import DeckResponse
from models.flashcard import Flashcard

router = APIRouter(prefix="/decks", tags=["Decks"])

def enrich_deck_stats(deck: Deck, db: Session):
    cards = db.query(Flashcard).filter(Flashcard.deck_id == deck.id).all()
    deck.known_cards = sum(1 for c in cards if c.review_count > 0)
    deck.due_cards = sum(1 for c in cards if c.next_review <= datetime.utcnow())
    
    types = {"diagram": 0, "chart": 0, "table": 0, "formula": 0}
    for c in cards:
        c_type = str(c.card_type)
        if c_type in types:
            types[c_type] += 1
        else:
            types[c_type] = 1
    deck.card_types = types
    return deck

@router.get("/", response_model=List[DeckResponse])
def get_all_decks(db: Session = Depends(get_db)):
    # Lấy danh sách tất cả các bộ flashcard kèm tiến độ
    decks = db.query(Deck).order_by(Deck.created_at.desc()).all()
    for deck in decks:
        enrich_deck_stats(deck, db)
    return decks

@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return enrich_deck_stats(deck, db)

@router.delete("/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    db.delete(deck)
    db.commit()
    return {"message": "Deck deleted successfully"}

@router.get("/{deck_id}/cards")
def get_all_cards_in_deck(deck_id: int, db: Session = Depends(get_db)):
    """API lấy toàn bộ danh sách thẻ thuộc về một bộ bài cụ thể."""
    cards = db.query(Flashcard).filter(Flashcard.deck_id == deck_id).all()
    return cards