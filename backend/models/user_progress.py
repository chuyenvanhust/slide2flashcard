from typing import Any
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Any = Column(Integer, primary_key=True, index=True)
    deck_id: Any = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_count: Any = Column(Integer, default=0)
    known_count: Any = Column(Integer, default=0)
    due_count: Any = Column(Integer, default=0)

    # Relationships
    deck = relationship("Deck", back_populates="progress")