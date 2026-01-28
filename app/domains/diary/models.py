from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Diary(Base):
    """일기 및 AI 분석 결과 저장 테이블"""
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # [은수] 유저 연결
    uuid = Column(String(36), unique=True, index=True)
    audio_path = Column(String(255), nullable=False)

    # [성률] 자동 일기 생성 관련 컬럼
    title = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    emotion_label = Column(String(50), index=True, nullable=True)
    emotion_score = Column(JSON, nullable=True)
    status = Column(String(20), default="PENDING", index=True) # PENDING, PROCESSING, COMPLETED, FAILED
    model_version = Column(String(50), default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 관계 설정
    user = relationship("User", back_populates="diaries")
    feedbacks = relationship(
        "Feedback",
        back_populates="diary",
        cascade="all, delete-orphan",
    )