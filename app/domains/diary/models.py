from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Diary(Base):
    """일기 및 AI 분석 결과 저장 테이블"""
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    uuid = Column(String(36), unique=True, index=True)
    audio_path = Column(String(255), nullable=False)

    title = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    advice = Column(Text, nullable=True)

    # [New] 현재 진행 상황을 사용자에게 알려줄 메시지 저장
    process_message = Column(String(255), nullable=True, default="분석 대기 중...")

    emotion_label = Column(String(50), index=True, nullable=True)
    emotion_score = Column(JSON, nullable=True)
    status = Column(String(20), default="PENDING", index=True)
    model_version = Column(String(50), default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="diaries")
    feedbacks = relationship(
        "Feedback",
        back_populates="diary",
        cascade="all, delete-orphan",
    )
