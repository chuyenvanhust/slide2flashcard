from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from core.dependencies import get_db
from models.deck import Deck
from schemas.deck import DeckResponse, DeckCreate, DeckUpdate, TransferRequest
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

@router.post("/", response_model=DeckResponse)
def create_deck(deck_in: DeckCreate, db: Session = Depends(get_db)):
    new_deck = Deck(name=deck_in.name)
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    return enrich_deck_stats(new_deck, db)

@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(deck_id: int, deck_in: DeckUpdate, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    deck.name = deck_in.name
    db.commit()
    db.refresh(deck)
    return enrich_deck_stats(deck, db)

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

@router.post("/cards/transfer")
def transfer_cards(req: TransferRequest, db: Session = Depends(get_db)):
    target_id = req.target_deck_id
    if target_id is None and req.target_deck_name:
        new_deck = Deck(name=req.target_deck_name)
        db.add(new_deck)
        db.commit()
        db.refresh(new_deck)
        target_id = new_deck.id
        
    if target_id is None:
        raise HTTPException(status_code=400, detail="Must provide target_deck_id or target_deck_name")

    target_deck = db.query(Deck).filter(Deck.id == target_id).first()
    if not target_deck:
        raise HTTPException(status_code=404, detail="Target deck not found")

    cards = db.query(Flashcard).filter(Flashcard.id.in_(req.card_ids)).all()
    
    if req.action == "move":
        for card in cards:
            old_deck = db.query(Deck).filter(Deck.id == card.deck_id).first()
            if old_deck and old_deck.total_cards > 0:
                old_deck.total_cards -= 1
            card.deck_id = target_id
            target_deck.total_cards += 1
    elif req.action == "copy":
        for card in cards:
            new_card = Flashcard(
                deck_id=target_id,
                image_path=card.image_path,
                back_text=card.back_text,
                card_type=card.card_type,
                source_page=card.source_page,
                source_file=card.source_file,
                confidence=card.confidence
            )
            db.add(new_card)
            target_deck.total_cards += 1
            
    db.commit()
    return {"message": f"Successfully {req.action}ed {len(cards)} cards"}