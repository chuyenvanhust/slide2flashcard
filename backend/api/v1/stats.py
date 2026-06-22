import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from core.dependencies import get_db
from models.review import Review
from models.flashcard import Flashcard
from models.deck import Deck

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/summary")
async def get_stats_summary(db: Session = Depends(get_db)):
    # 1. Lịch sử ôn tập 14 ngày qua
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    reviews_by_date_query = db.query(
        func.date(Review.reviewed_at).label('date'),
        func.count(Review.id).label('count')
    ).filter(
        Review.reviewed_at >= fourteen_days_ago
    ).group_by(
        func.date(Review.reviewed_at)
    ).order_by(
        func.date(Review.reviewed_at)
    ).all()
    
    # 2. Tỉ lệ retention
    total_reviews = db.query(func.count(Review.id)).scalar() or 0
    retained_reviews = db.query(func.count(Review.id)).filter(
        Review.rating.in_(['easy', 'medium'])
    ).scalar() or 0
    retention_rate = round((retained_reviews / total_reviews * 100), 1) if total_reviews > 0 else 0

    # 3. Card type breakdown
    type_counts = db.query(
        Flashcard.card_type,
        func.count(Flashcard.id)
    ).group_by(Flashcard.card_type).all()

    # 4. Deck progress
    decks = db.query(Deck).all()
    deck_progress = []
    for d in decks:
        # Simplify name by removing UUID and paths
        import re
        clean_name = d.name.split('/')[-1].split('\\')[-1]
        clean_name = re.sub(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}_', '', clean_name)
        
        known = db.query(func.count(Flashcard.id)).filter(
            Flashcard.deck_id == d.id,
            Flashcard.review_count > 0
        ).scalar() or 0
        
        deck_progress.append({
            "name": clean_name,
            "known": known,
            "total": d.total_cards
        })

    return {
        "reviews_by_date": [{"date": r.date, "count": r.count} for r in reviews_by_date_query],
        "retention_rate": retention_rate,
        "type_breakdown": [{"type": t[0], "count": t[1]} for t in type_counts],
        "deck_progress": deck_progress
    }
