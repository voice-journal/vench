import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Diary
from app.services.stt_service import transcribe
from app.services.emotion_service import analyze_emotion
from app.services.summary_service import summary_service

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_audio_task(diary_id: int):
    db: Session = SessionLocal()
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary: return

        diary.status = "PROCESSING"
        db.commit()

        # 1. STT
        transcript = transcribe(diary.audio_path)
        if not transcript:
            diary.status = "FAILED"
            db.commit()
            return
        diary.transcript = transcript

        # 2. 감정 분석
        emotion_res = analyze_emotion(transcript)
        diary.emotion_label = emotion_res["label"]
        diary.emotion_score = emotion_res["all_scores"]

        # 3. 요약 및 제목 생성
        summary_text = summary_service.generate_summary(transcript)
        diary.summary = summary_text
        diary.title = summary_service.generate_title(summary_text)

        diary.status = "COMPLETED"
        db.commit()
    except Exception as e:
        print(f"Task Error: {e}")
        diary.status = "FAILED"
        db.commit()
    finally:
        db.close()
