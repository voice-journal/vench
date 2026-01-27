from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
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

    # ✅ 피드백 연관
    feedbacks = relationship(
        "Feedback",
        back_populates="diary",
        cascade="all, delete-orphan",
    )

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    diary_id = Column(
        Integer,
        ForeignKey("diaries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating = Column(Integer, nullable=False)   # 1~5
    comment = Column(Text, nullable=True)

    # ✅ Diary와 동일하게 DB에서 시간 찍게 통일
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # ✅ 오타 수정: relation -> relationship
    diary = relationship("Diary", back_populates="feedbacks")