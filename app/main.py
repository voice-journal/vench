import logging
import os
import shutil
import uuid
import subprocess  # 포맷 변환을 위한 라이브러리 추가

from fastapi import BackgroundTasks, Depends, FastAPI, File, UploadFile, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.models import Diary
from app.services.emotion_service import analyze_emotion
from app.services.stt_service import transcribe # 팀원 B님의 STT 엔진

# DB 초기화
Base.metadata.create_all(bind=engine)

# 로깅 설정 (Loki 연동용)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vench")

app = FastAPI()
# Prometheus 모니터링 활성화
Instrumentator().instrument(app).expose(app)

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_audio_task(diary_id: int):
    """비동기 작업: STT -> 감정 분석 -> 결과 저장"""
    db = SessionLocal()
    logger.info(f"Task Start: diary_id={diary_id}")
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary:
            return

        audio_path = diary.audio_path

        # [Bridge Logic] WebM 포맷을 Whisper가 선호하는 Wav로 변환
        if audio_path.endswith(".webm"):
            logger.info("🔄 WebM 포맷 감지: Wav 변환 시작...")
            wav_path = audio_path.replace(".webm", ".wav")
            # FFmpeg를 이용한 16kHz 모노 변환 (추론 속도 최적화)
            subprocess.run([
                'ffmpeg', '-y', '-i', audio_path,
                '-ar', '16000', '-ac', '1', wav_path
            ], check=True, capture_output=True)
            audio_path = wav_path
            logger.info("✅ 변환 완료")

        # 1. STT 실행 (B님의 코드 호출)
        logger.info("🎙️ STT 분석 시작...")
        transcript = transcribe(audio_path)

        if not transcript or len(transcript) < 2:
            logger.warning("⚠️ 인식된 텍스트가 너무 짧거나 비어있습니다.")
            diary.status = "FAILED"
            db.commit()
            return

        diary.transcript = transcript

        # 2. 감정 분석 (DeBERTa 모델)
        logger.info("🤖 AI 감정 분석 시작...")
        emotion_result = analyze_emotion(diary.transcript)

        # 3. 결과 저장
        diary.emotion_label = emotion_result["label"]
        diary.emotion_score = emotion_result["all_scores"]
        diary.status = "COMPLETED"

        db.commit()
        logger.info(f"✅ 분석 최종 완료: {diary.emotion_label}")

    except Exception as e:
        logger.error(f"❌ 분석 중 에러 발생: {e}")
        try:
            diary_error = db.query(Diary).filter(Diary.id == diary_id).first()
            if diary_error:
                diary_error.status = "FAILED"
                db.commit()
        except:
            pass
    finally:
        db.close()

@app.post("/diaries")
async def create_diary(
        bg_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    file_uuid = str(uuid.uuid4())
    save_path = f"{UPLOAD_DIR}/{file_uuid}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_diary = Diary(uuid=file_uuid, audio_path=save_path, status="PENDING")
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)

    # 비동기 큐 등록 (사용자는 즉시 응답 받음)
    bg_tasks.add_task(process_audio_task, new_diary.id)

    return {"message": "Accepted", "id": new_diary.id}

@app.get("/diaries/{diary_id}")
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    return {
        "id": diary.id,
        "status": diary.status,
        "transcript": diary.transcript,
        "emotion_label": diary.emotion_label,
        "emotion_score": diary.emotion_score,
    }

@app.get("/reports/weekly")
def get_weekly_report(db: Session = Depends(get_db)):
    """감정 분포 집계 (가로 레이블 UI용)"""
    stats = (
        db.query(Diary.emotion_label, func.count(Diary.id))
        .filter(Diary.status == "COMPLETED")
        .group_by(Diary.emotion_label)
        .all()
    )
    return {label: count for label, count in stats if label}
