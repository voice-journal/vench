from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.domains.diary.models import Diary
from app.domains.feedback.analyzers.kiwi_analyzer import KiwiAnalyzer
from app.domains.feedback.models import Feedback, FeedbackAnalysisStatus, FeedbackKeyword

_analyzer = KiwiAnalyzer(top_n=3, model_version="morph-v1")


@dataclass(frozen=True)
class CreateFeedbackCommand:
    diary_id: int
    rating: int
    comment: Optional[str]


@dataclass(frozen=True)
class CreateFeedbackResult:
    id: int
    diary_id: int
    rating: int
    comment: Optional[str]
    user_category: Optional[str]
    analysis_status: str
    corrected_emotion: Optional[str]
    created_at: datetime


def create_feedback(
    db: Session,
    cmd: CreateFeedbackCommand,
    *,
    user_category,
    corrected_emotion: str | None,
    background_tasks: BackgroundTasks | None,
) -> CreateFeedbackResult:
    # 1) rating 검증
    if not (1 <= cmd.rating <= 5):
        raise HTTPException(status_code=400, detail="rating must be between 1 and 5")

    # 2) comment 정리/검증
    normalized_comment = cmd.comment.strip() if cmd.comment else None
    if normalized_comment and len(normalized_comment) > 5000:
        raise HTTPException(status_code=400, detail="comment is too long")

    # 3) Diary 존재 확인
    diary = db.query(Diary).filter(Diary.id == cmd.diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    # 4) 분석 완료 후에만 허용
    if getattr(diary, "status", None) not in ("COMPLETED", "READY"):
        raise HTTPException(status_code=409, detail="Diary analysis is not completed yet")

    # 5) comment 여부에 따라 초기 상태 결정
    initial_status = (
        FeedbackAnalysisStatus.PENDING
        if (normalized_comment and normalized_comment.strip())
        else FeedbackAnalysisStatus.SKIPPED
    )

    # 6) 저장
    feedback = Feedback(
        diary_id=cmd.diary_id,
        rating=cmd.rating,
        comment=normalized_comment,
        user_category=user_category,
        analysis_status=initial_status,
        corrected_emotion=corrected_emotion,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # 7) ✅ 비동기 분석은 저장 성공 이후에만
    if background_tasks and initial_status == FeedbackAnalysisStatus.PENDING:
        background_tasks.add_task(_analyze_feedback_keywords, feedback.id)

    # 8) ORM → DTO 변환해서 반환
    return CreateFeedbackResult(
        id=feedback.id,
        diary_id=feedback.diary_id,
        rating=feedback.rating,
        comment=feedback.comment,
        user_category=feedback.user_category,
        analysis_status=feedback.analysis_status,
        corrected_emotion=feedback.corrected_emotion,
        created_at=feedback.created_at,
    )


def _analyze_feedback_keywords(feedback_id: int) -> None:
    """
    BackgroundTasks는 request context 밖에서 실행되므로
    여기서는 "새 DB 세션"을 열어야 함.
    """
    from app.core.database import SessionLocal  # 프로젝트에 맞게 경로 조정

    db = SessionLocal()
    try:
        feedback: Feedback | None = db.get(Feedback, feedback_id)
        if not feedback:
            return

        # comment가 없으면 분석할 게 없음
        if not feedback.comment or not feedback.comment.strip():
            feedback.analysis_status = FeedbackAnalysisStatus.SKIPPED
            db.commit()
            return

        # 이미 처리됐으면 스킵(중복 실행 방지)
        if feedback.analysis_status in (
            FeedbackAnalysisStatus.DONE,
            FeedbackAnalysisStatus.FAILED,
            FeedbackAnalysisStatus.SKIPPED,
        ):
            return

        result = _analyzer.analyze(feedback.comment)

        # 기존 키워드 제거 후 재삽입(재처리 대비)
        db.query(FeedbackKeyword).filter(FeedbackKeyword.feedback_id == feedback_id).delete()

        for kw in result.keywords:
            db.add(
                FeedbackKeyword(
                    feedback_id=feedback_id,
                    keyword=kw,
                    model_version=result.model_version,
                )
            )

        feedback.analysis_status = result.status
        db.commit()

    except Exception:
        # 실패해도 "피드백 저장 자체"는 망치면 안 됨 → 상태만 FAILED로
        try:
            feedback = db.get(Feedback, feedback_id)
            if feedback and feedback.analysis_status not in (
                FeedbackAnalysisStatus.DONE,
                FeedbackAnalysisStatus.SKIPPED,
            ):
                feedback.analysis_status = FeedbackAnalysisStatus.FAILED
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
