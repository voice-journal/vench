from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.domains.feedback.models import FeedbackCategory, FeedbackAnalysisStatus


class CreateFeedbackRequest(BaseModel):
    diary_id: int = Field(..., ge=1)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=5000)

    user_category: Optional[FeedbackCategory] = None

    # ✅ 확장 포인트 (프론트가 나중에 보내면 저장)
    corrected_emotion: Optional[str] = Field(default=None, max_length=50)


class CreateFeedbackResponse(BaseModel):
    id: int
    diary_id: int
    rating: int
    comment: Optional[str]
    user_category: Optional[FeedbackCategory]
    analysis_status: FeedbackAnalysisStatus
    corrected_emotion: Optional[str]
    created_at: datetime


class AdminFeedbackRow(BaseModel):
    id: int
    diary_id: int
    rating: int
    comment: Optional[str]
    user_category: Optional[FeedbackCategory]
    analysis_status: FeedbackAnalysisStatus
    created_at: datetime


class AdminSummaryResponse(BaseModel):
    total_count: int
    average_rating: float
    low_rating_ratio: float  # (rating <= 2) / total
    delta_7_vs_30: dict  # {"total_count": {...}, "average_rating": {...}, "low_rating_ratio": {...}}


class CategoryDistributionItem(BaseModel):
    category: str
    count: int
    ratio: float


class KeywordTopItem(BaseModel):
    keyword: str
    count: int