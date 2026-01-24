from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Diary(Base):
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    audio_path = Column(String(255), nullable=False)
    transcript = Column(Text, nullable=True)
    emotion_label = Column(String(50), index=True, nullable=True)
    emotion_score = Column(JSON, nullable=True)
    status = Column(String(20), default="PENDING", index=True) # PENDING, PROCESSING, COMPLETED, FAILED
    model_version = Column(String(50), default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
