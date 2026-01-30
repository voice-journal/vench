from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
import os

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.feedback.models import Feedback, FeedbackKeyword, FeedbackCategory
from app.domains.feedback.schema import (
    AdminFeedbackRow,
    AdminSummaryResponse,
    CategoryDistributionItem,
    KeywordTopItem,
    CreateFeedbackRequest,
    CreateFeedbackResponse,
)
from app.domains.feedback.service import create_feedback
from app.domains.feedback.service import CreateFeedbackCommand

router = APIRouter()


# ------------------------
# Common helpers
# ------------------------

def _require_admin(x_admin_token: Optional[str]) -> None:
    expected = os.getenv("ADMIN_TOKEN")
    # expected가 설정돼 있으면 반드시 매칭되어야 함
    if expected and x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _range_days(days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


# ------------------------
# Admin APIs
# ------------------------

@router.get("/summary", response_model=AdminSummaryResponse)
def feedback_summary(
    days: int = 30,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    _require_admin(x_admin_token)

    since = _range_days(days)
    base_q = db.query(Feedback).filter(Feedback.created_at >= since)

    total = base_q.count()
    avg_rating = float(base_q.with_entities(func.avg(Feedback.rating)).scalar() or 0.0)
    low_cnt = int(base_q.filter(Feedback.rating <= 2).count())
    low_ratio = float(low_cnt / total) if total > 0 else 0.0

    # ✅ 7일 vs 30일 비교(상대 변화)
    q7 = db.query(Feedback).filter(Feedback.created_at >= _range_days(7))
    q30 = db.query(Feedback).filter(Feedback.created_at >= _range_days(30))

    def _pack(q):
        t = q.count()
        a = float(q.with_entities(func.avg(Feedback.rating)).scalar() or 0.0)
        l = int(q.filter(Feedback.rating <= 2).count())
        r = float(l / t) if t > 0 else 0.0
        return {"total": t, "avg": a, "low_ratio": r}

    s7 = _pack(q7)
    s30 = _pack(q30)

    def _delta(a, b):
        if b == 0:
            return None
        return (a - b) / b

    delta = {
        "total_count": {
            "v7": s7["total"],
            "v30": s30["total"],
            "rate": _delta(s7["total"], s30["total"]),
        },
        "average_rating": {
            "v7": s7["avg"],
            "v30": s30["avg"],
            "rate": _delta(s7["avg"], s30["avg"]),
        },
        "low_rating_ratio": {
            "v7": s7["low_ratio"],
            "v30": s30["low_ratio"],
            "rate": _delta(s7["low_ratio"], s30["low_ratio"]),
        },
    }

    return AdminSummaryResponse(
        total_count=total,
        average_rating=avg_rating,
        low_rating_ratio=low_ratio,
        delta_7_vs_30=delta,
    )


@router.get("/categories", response_model=list[CategoryDistributionItem])
def category_distribution(
    days: int = 30,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    _require_admin(x_admin_token)

    since = _range_days(days)
    rows = (
        db.query(Feedback.user_category, func.count(Feedback.id))
        .filter(Feedback.created_at >= since)
        .group_by(Feedback.user_category)
        .all()
    )

    total = sum(int(c) for _, c in rows) or 0
    result: list[CategoryDistributionItem] = []

    for cat, cnt in rows:
        name = cat.value if cat else "UNSPECIFIED"
        c = int(cnt)
        result.append(
            CategoryDistributionItem(
                category=name,
                count=c,
                ratio=(c / total if total else 0.0),
            )
        )

    result.sort(key=lambda x: x.count, reverse=True)
    return result


@router.get("/keywords/top", response_model=list[KeywordTopItem])
def top_keywords(
    days: int = 30,
    category: Optional[FeedbackCategory] = None,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    _require_admin(x_admin_token)

    since = _range_days(days)

    q = (
        db.query(FeedbackKeyword.keyword, func.count(FeedbackKeyword.id).label("cnt"))
        .join(Feedback, Feedback.id == FeedbackKeyword.feedback_id)
        .filter(Feedback.created_at >= since)
    )
    if category:
        q = q.filter(Feedback.user_category == category)

    rows = (
        q.group_by(FeedbackKeyword.keyword)
        .order_by(func.count(FeedbackKeyword.id).desc())
        .limit(20)
        .all()
    )
    return [KeywordTopItem(keyword=k, count=int(c)) for k, c in rows]


@router.get("", response_model=list[AdminFeedbackRow])
def list_feedbacks(
    days: int = 30,
    category: Optional[FeedbackCategory] = None,
    low_only: bool = False,
    q: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    db: Session = Depends(get_db),
):
    _require_admin(x_admin_token)

    since = _range_days(days)
    query = db.query(Feedback).filter(Feedback.created_at >= since)

    if category:
        query = query.filter(Feedback.user_category == category)
    if low_only:
        query = query.filter(Feedback.rating <= 2)
    if q:
        query = query.filter(Feedback.comment.isnot(None)).filter(Feedback.comment.like(f"%{q}%"))

    rows = query.order_by(Feedback.created_at.desc()).limit(500).all()
    return [
        AdminFeedbackRow(
            id=f.id,
            diary_id=f.diary_id,
            rating=f.rating,
            comment=f.comment,
            user_category=f.user_category,
            analysis_status=f.analysis_status,
            created_at=f.created_at,
        )
        for f in rows
    ]


# ------------------------
# User APIs
# ------------------------

@router.post("", response_model=CreateFeedbackResponse)
def create_feedback_v2(
    req: CreateFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    cmd = CreateFeedbackCommand(
        diary_id=req.diary_id,
        rating=req.rating,
        comment=req.comment,
    )

    feedback = create_feedback(
        db,
        cmd,
        user_category=req.user_category,
        corrected_emotion=req.corrected_emotion,
        background_tasks=background_tasks,
    )

    return CreateFeedbackResponse(
        id=feedback.id,
        diary_id=feedback.diary_id,
        rating=feedback.rating,
        comment=feedback.comment,
        user_category=feedback.user_category,
        analysis_status=feedback.analysis_status,
        corrected_emotion=feedback.corrected_emotion,
        created_at=feedback.created_at,
    )
