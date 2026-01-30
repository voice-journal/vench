import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.metrics import TOTAL_USERS, TOTAL_DIARIES, EMOTION_COUNT
from app.domains.auth.models import User
from app.domains.diary.models import Diary

logger = logging.getLogger("Vench.Monitoring")

# Vench v2.0에서 지원하는 8가지 핵심 감정
ALL_EMOTIONS = [
    "기쁨", "슬픔", "분노", "불안", "평온",
    "피로", "뿌듯", "설렘"
]

def update_business_metrics(db: Session):
    """
    DB에서 최신 통계를 조회하여 Prometheus 메트릭을 업데이트합니다.
    (감정 분포: 단순 개수가 아닌 감정 점수 총합으로 집계)
    """
    try:
        # 1. 총 사용자 수 집계
        user_count = db.query(func.count(User.id)).scalar()
        TOTAL_USERS.set(user_count)

        # 2. 누적 일기 수 집계
        diary_count = db.query(func.count(Diary.id)).scalar()
        TOTAL_DIARIES.set(diary_count)

        # 3. 감정별 분포 집계 (점수 기반 누적)
        # 초기화: 모든 감정 0.0으로 셋팅 (데이터가 없어도 0으로 표시되도록)
        stats = {emotion: 0.0 for emotion in ALL_EMOTIONS}

        # DB 조회: 완료된 일기의 emotion_score(JSON) 가져오기
        diaries = (
            db.query(Diary.emotion_score)
            .filter(Diary.status == "COMPLETED")
            .filter(Diary.emotion_score != None)
            .all()
        )

        # Python 레벨에서 JSON 파싱 및 점수 합산
        for row in diaries:
            emotion_data = row.emotion_score
            if not emotion_data or not isinstance(emotion_data, list):
                continue

            for item in emotion_data:
                label = item.get("label")
                score = item.get("score")

                # 유효한 감정 라벨이고 점수가 있는 경우 합산
                if label in stats and isinstance(score, (int, float)):
                    stats[label] += score

        # 4. Prometheus 메트릭 업데이트
        # 소수점 1자리로 반올림하여 설정
        for label, score_sum in stats.items():
            EMOTION_COUNT.labels(label=label).set(round(score_sum, 1))

        # logger.info(f"✅ Metrics Updated: Users={user_count}, Diaries={diary_count}")

    except Exception as e:
        logger.error(f"❌ Failed to update business metrics: {e}")
