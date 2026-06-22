from typing import Any
from sqlalchemy import Column, String, Integer
from core.database import Base

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Any = Column(String, primary_key=True, index=True)
    status: Any = Column(String, nullable=False, default="pending")  # pending, processing, done, failed
    progress: Any = Column(Integer, default=0)
    message: Any = Column(String, nullable=True)
    error: Any = Column(String, nullable=True)
