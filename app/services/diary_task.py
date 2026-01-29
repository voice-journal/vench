import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.domains.diary.models import Diary

from app.services.stt_service import transcribe
from app.services.emotion_service import analyze_emotion
from app.services.diary_generation_service import diary_service

def process_audio_task(diary_id: int):
    print(f"🔄 Task Started for Diary ID: {diary_id}")
    db: Session = SessionLocal()
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary: return

        # 0. 시작
        diary.status = "PROCESSING"
        diary.process_message = "🎧 오디오 파일을 확인하고 있어요..."
        db.commit() # 중간 저장

        # 1. STT
        diary.process_message = "🎤 목소리를 글로 옮기고 있어요... (STT)"
        db.commit() # 중간 저장

        transcript = transcribe(diary.audio_path)
        if not transcript:
            print("❌ STT Result Empty")
            diary.status = "FAILED"
            diary.process_message = "음성 인식에 실패했습니다."
            db.commit()
            return
        diary.transcript = transcript

        # 2. 감정 분석
        diary.process_message = "🧠 목소리에 담긴 감정을 분석하고 있어요..."
        db.commit() # 중간 저장

        emotion_res = analyze_emotion(transcript)
        diary.emotion_label = emotion_res["label"]
        diary.emotion_score = emotion_res["all_scores"]

        # 3. 일기 및 위로 메시지 생성
        print("✍️ Generating Diary & Advice...")

        # 3-1. 일기 본문
        diary.process_message = "✍️ 오늘의 이야기를 일기로 다듬고 있어요..."
        db.commit() # 중간 저장
        generated_diary = diary_service.generate_diary(transcript, diary.emotion_label)
        diary.summary = generated_diary

        # 3-2. 제목
        diary.title = diary_service.generate_title(generated_diary)

        # 3-3. 위로 메시지
        diary.process_message = "💌 당신을 위한 위로의 한마디를 고민 중이에요..."
        db.commit() # 중간 저장
        diary.advice = diary_service.generate_advice(transcript, diary.emotion_label)

        # 4. 완료
        diary.status = "COMPLETED"
        diary.process_message = "✅ 분석이 완료되었습니다!"
        db.commit()
        print("✅ Task Completed!")

    except Exception as e:
        print(f"🔥 Task Error: {e}")
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if diary:
            diary.status = "FAILED"
            diary.process_message = "서버 오류가 발생했습니다."
            db.commit()
    finally:
        db.close()
