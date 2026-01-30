from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    String,
    DateTime,
    Enum,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.core.database import Base


# =========================
# Enum 정의
# =========================

class FeedbackCategory(PyEnum):
    STT_ACCURACY = "STT_ACCURACY"
    PERFORMANCE = "PERFORMANCE"
    UX_UI = "UX_UI"
    BUG = "BUG"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    OTHER = "OTHER"


class FeedbackAnalysisStatus(PyEnum):
    PENDING = "PENDING"
    DONE = "DONE"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# =========================
# Feedback (기존 + 확장)
# =========================

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

    # ✅ 사용자가 선택한 대표 카테고리 (선택)
    user_category = Column(
        Enum(FeedbackCategory, native_enum=False),
        nullable=True,
        index=True,
    )

    # ✅ 코멘트 분석 상태
    analysis_status = Column(
        Enum(FeedbackAnalysisStatus, native_enum=False),
        nullable=False,
        default=FeedbackAnalysisStatus.PENDING,
        server_default=FeedbackAnalysisStatus.PENDING.value,
        index=True,
    )

    # ✅ 확장 포인트: 감정 교정 (프론트 나중에 붙이기용)
    corrected_emotion = Column(String(50), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # 기존 관계 (유지)
    diary = relationship("Diary", back_populates="feedbacks")

    # ✅ 키워드 관계 (1:N)
    keywords = relationship(
        "FeedbackKeyword",
        back_populates="feedback",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# =========================
# FeedbackKeyword (신규, 최소형)
# =========================

class FeedbackKeyword(Base):
    __tablename__ = "feedback_keywords"

    id = Column(Integer, primary_key=True)

    feedback_id = Column(
        Integer,
        ForeignKey("feedbacks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    keyword = Column(String(80), nullable=False, index=True)

    # 어떤 분석기로 뽑은 키워드인지 (v1 → v2 비교 가능)
    model_version = Column(String(30), nullable=False, default="morph-v1")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    feedback = relationship("Feedback", back_populates="keywords")


# =========================
# Index (집계/드릴다운 최적화)
# =========================

Index(
    "ix_feedback_keywords_feedback_id_keyword",
    FeedbackKeyword.feedback_id,
    FeedbackKeyword.keyword,
)