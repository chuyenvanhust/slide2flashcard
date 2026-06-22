from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.dependencies import get_db
from models.flashcard import Flashcard
from models.review import Review
from schemas.review import ReviewCreate, ReviewResponse
from services.spaced_repetition import calculate_sm2

router = APIRouter(prefix="/cards", tags=["Reviews"])

@router.post("/{card_id}/review", response_model=ReviewResponse)
def submit_review(card_id: int, review_data: ReviewCreate, db: Session = Depends(get_db)):
    # 1. Lấy thông tin thẻ
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # 2. Lấy dữ liệu SM-2 hiện tại (Bọc lỗi NoneType)
    current_interval = card.interval or 0
    current_ease = card.ease_factor or 2.5

    # 3. Chạy thuật toán SM-2
    next_review, new_interval, new_ease = calculate_sm2(
        rating=review_data.rating,
        current_interval=current_interval,
        current_ease=current_ease
    )

    # 4. Lưu kết quả review mới vào DB
    new_review = Review(
        card_id=card_id,
        rating=review_data.rating,
        reviewed_at=datetime.utcnow(),
        next_review=next_review,
        interval=new_interval,
        ease_factor=new_ease
    )
    db.add(new_review)

    # 5. Cập nhật trực tiếp thông tin lên thẻ Flashcard (Bọc lỗi NoneType)
    card.next_review = next_review
    card.interval = new_interval
    card.ease_factor = new_ease
    card.review_count = (card.review_count or 0) + 1
        
    db.commit()
    db.refresh(new_review)

    return new_review