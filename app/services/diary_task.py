# app/services/diary_task.py
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.domains.diary.models import Diary

# 서비스 임포트
from app.services.stt_service import transcribe
from app.services.emotion_service import analyze_emotion
# [변경] summary_service -> diary_generation_service
from app.services.diary_generation_service import diary_service

def process_audio_task(diary_id: int):
    print(f"🔄 Task Started for Diary ID: {diary_id}")
    db: Session = SessionLocal()
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary: return

        diary.status = "PROCESSING"
        db.commit()

        # 1. STT (Wav 변환 포함)
        transcript = transcribe(diary.audio_path)
        if not transcript:
            print("❌ STT Result Empty")
            diary.status = "FAILED"
            db.commit()
            return
        diary.transcript = transcript

        # 2. 감정 분석
        emotion_res = analyze_emotion(transcript)
        diary.emotion_label = emotion_res["label"]
        diary.emotion_score = emotion_res["all_scores"]

        # 3. [New] 일기 생성 (Gemma)
        print("✍️ Generating Diary...")
        generated_diary = diary_service.generate_diary(transcript, diary.emotion_label)
        diary.summary = generated_diary
        diary.title = diary_service.generate_title(generated_diary)

        diary.status = "COMPLETED"
        db.commit()
        print("✅ Task Completed!")

    except Exception as e:
        print(f"🔥 Task Error: {e}")
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if diary:
            diary.status = "FAILED"
            db.commit()
    finally:
        db.close()
