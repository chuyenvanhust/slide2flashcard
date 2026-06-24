from typing import Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Any = Column(Integer, primary_key=True, index=True)
    deck_id: Any = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    image_path: Any = Column(String, nullable=False)
    back_text: Any = Column(String, nullable=True)
    card_type: Any = Column(String, nullable=False)  # diagram, chart, table, formula
    source_page: Any = Column(Integer, nullable=False)
    confidence: Any = Column(Float, nullable=True)
    created_at: Any = Column(DateTime, default=datetime.utcnow)

    interval: Any = Column(Integer, default=0) # Khoảng cách ngày học tiếp theo
    ease_factor: Any = Column(Float, default=2.5) # Hệ số độ khó (E-factor)
    review_count: Any = Column(Integer, default=0) # Số lần đã ôn tập
    next_review: Any = Column(DateTime, default=datetime.utcnow)

    # Relationships
    deck = relationship("Deck", back_populates="flashcards")
    reviews = relationship("Review", back_populates="flashcard", cascade="all, delete-orphan")