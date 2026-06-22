from typing import Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id: Any = Column(Integer, primary_key=True, index=True)
    card_id: Any = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False)
    rating: Any = Column(String, nullable=False)  # easy, medium, hard, again
    reviewed_at: Any = Column(DateTime, default=datetime.utcnow)
    next_review: Any = Column(DateTime, nullable=False)  # Ngày đến hạn học tiếp theo
    interval: Any = Column(Integer, nullable=False)      # Khoảng thời gian (ngày)
    ease_factor: Any = Column(Float, nullable=False)     # Hệ số sụt giảm E-factor theo SM-2

    # Relationships
    flashcard = relationship("Flashcard", back_populates="reviews")