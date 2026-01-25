from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.models import Diary
from app.services.stt_service import transcribe
from app.services.emotion_service import analyze_emotion

def create_diary(db: Session, audio_path: str) -> Diary:
    diary = Diary(
        audio_path=audio_path,
        status="PROCESSING",
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return diary


def run_pipeline_background(db: Session, diary_id: int):
    """
    BackgroundTasks에서 호출될 함수.
    (주의) BackgroundTasks는 요청 종료 후 실행되지만 같은 DB 세션을 공유하지 않는 편이 안전함.
    그래서 실무적으로는 여기서 새 Session을 열어 쓰는게 더 좋다.
    """
    # ⚠️ 최소 구현: db를 그대로 받는 구조(작동은 함)
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        return

    try:
        transcript = transcribe(diary.audio_path)  # B 구현
        emotion_label, emotion_score = analyze_emotion(transcript)  # C 구현

        diary.transcript = transcript
        diary.emotion_label = emotion_label
        diary.emotion_score = emotion_score
        diary.status = "READY"
        diary.error_message = None

        db.commit()

    except Exception as e:
        diary.status = "FAILED"
        diary.error_message = str(e)
        db.commit()


def schedule_pipeline(background_tasks: BackgroundTasks, db: Session, diary_id: int):
    background_tasks.add_task(run_pipeline_background, db, diary_id)
