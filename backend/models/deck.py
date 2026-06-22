from typing import Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from core.database import Base

class Deck(Base):
    __tablename__ = "decks"

    id: Any = Column(Integer, primary_key=True, index=True)
    name: Any = Column(String, nullable=False)
    total_cards: Any = Column(Integer, default=0)
    created_at: Any = Column(DateTime, default=datetime.utcnow)

    # Quan hệ với Flashcard (Một Deck có nhiều Flashcards)
    flashcards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")