from sqlalchemy.orm import Session
from sqlalchemy import func
from app.domains.diary.models import Diary

def get_weekly_emotion_stats(db: Session):
    """
    전체 일기의 감정별 개수를 집계하여 반환합니다.
    (추후 '최근 7일' 필터링 등을 추가할 수 있습니다.)
    """
    # SQL: SELECT emotion_label, COUNT(*) FROM diaries GROUP BY emotion_label
    results = (
        db.query(Diary.emotion_label, func.count(Diary.id))
        .filter(Diary.status == "COMPLETED")  # 완료된 일기만
        .filter(Diary.emotion_label != None)
        .group_by(Diary.emotion_label)
        .all()
    )

    # Dict 변환
    stats = {label: count for label, count in results}
    return stats
