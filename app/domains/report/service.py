from sqlalchemy.orm import Session
from app.domains.diary.models import Diary

# Vench v2.0에서 지원하는 8가지 핵심 감정
ALL_EMOTIONS = [
    "기쁨", "슬픔", "분노", "불안", "평온",
    "피로", "뿌듯", "설렘"
]

def get_weekly_emotion_stats(db: Session):
    """
    전체 일기의 감정별 점수(Score)를 누적 집계하여 반환합니다.
    단순 개수(Count)가 아니라, 각 일기에 포함된 세부 감정 비중을 모두 합산합니다.
    예: 기쁨 0.8 + 슬픔 0.2 인 경우, 기쁨 통계에 0.8, 슬픔 통계에 0.2가 누적됩니다.
    """

    # 1. 8가지 감정을 모두 0.0으로 초기화 (점수 누적을 위해 float 사용)
    stats = {emotion: 0.0 for emotion in ALL_EMOTIONS}

    # 2. DB 조회 (모든 완료된 일기의 세부 감정 점수 가져오기)
    # emotion_score 컬럼은 JSON 타입이며, [{'label': '기쁨', 'score': 0.9}, ...] 형태의 리스트가 저장됩니다.
    diaries = (
        db.query(Diary.emotion_score)
        .filter(Diary.status == "COMPLETED")
        .filter(Diary.emotion_score != None)
        .all()
    )

    # 3. 감정 점수 누적 (Python 레벨에서 집계)
    # 기존에는 1등 감정(label)만 카운트했지만, 이제는 모든 감정의 점수(score)를 합산합니다.
    for row in diaries:
        emotion_data = row.emotion_score
        # JSON 데이터가 리스트인지 확인 (유효성 검사)
        if not emotion_data or not isinstance(emotion_data, list):
            continue

        for item in emotion_data:
            label = item.get("label")
            score = item.get("score")

            # 유효한 감정 라벨이고 점수가 있는 경우 합산
            if label in stats and isinstance(score, (int, float)):
                stats[label] += score

    # 4. 소수점 정리 (선택 사항)
    # 누적된 점수를 반올림하여 깔끔하게 만듭니다.
    for k, v in stats.items():
        stats[k] = round(v, 1)

    return stats
