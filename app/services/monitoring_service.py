import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.metrics import TOTAL_USERS, TOTAL_DIARIES, EMOTION_COUNT
from app.domains.auth.models import User
from app.domains.diary.models import Diary

logger = logging.getLogger("Vench.Monitoring")

def update_business_metrics(db: Session):
    """
    DB에서 최신 통계를 조회하여 Prometheus 메트릭을 업데이트합니다.
    """
    try:
        # 1. 총 사용자 수 집계
        user_count = db.query(func.count(User.id)).scalar()
        TOTAL_USERS.set(user_count)

        # 2. 누적 일기 수 집계
        diary_count = db.query(func.count(Diary.id)).scalar()
        TOTAL_DIARIES.set(diary_count)

        # 3. 감정별 분포 집계
        # SQL: SELECT emotion_label, COUNT(*) FROM diaries WHERE status='COMPLETED' GROUP BY emotion_label
        emotion_stats = (
            db.query(Diary.emotion_label, func.count(Diary.id))
            .filter(Diary.status == "COMPLETED")
            .filter(Diary.emotion_label != None)
            .group_by(Diary.emotion_label)
            .all()
        )

        # 라벨별로 수치 업데이트
        if emotion_stats:
            for label, count in emotion_stats:
                EMOTION_COUNT.labels(label=label).set(count)

        # logger.info(f"✅ Metrics Updated: Users={user_count}, Diaries={diary_count}") # (너무 시끄러우면 주석 처리)

    except Exception as e:
        logger.error(f"❌ Failed to update business metrics: {e}")
