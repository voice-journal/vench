import logging
import os
import shutil
import uuid
import subprocess

from fastapi import BackgroundTasks, Depends, FastAPI, File, UploadFile, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from app.database import Base, SessionLocal, engine, get_db
from app.models import Diary, Feedback, User
from app.services.emotion_service import analyze_emotion
from app.services.stt_service import transcribe
from app.services.feedback import create_feedback, CreateFeedbackCommand
# from app.services.summary_service import generate_summary, generate_title # [성률] 추후 생성 예정
# from app.services.auth_service import hash_password, create_jwt # [은수] 추후 생성 예정

# DB 초기화
Base.metadata.create_all(bind=engine)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vench")

app = FastAPI()
Instrumentator().instrument(app).expose(app)

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- [은수] 인증 관련 스키마 및 API ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

@app.post("/auth/register")
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """회원가입 API"""
    # TODO: 비밀번호 해싱 및 유저 저장 로직 구현
    return {"message": "User registered successfully"}

@app.post("/auth/login")
async def login(db: Session = Depends(get_db)):
    """로그인 및 JWT 발급 API"""
    # TODO: 인증 및 토큰 생성 로직 구현
    return {"access_token": "token_example", "token_type": "bearer"}


# --- [성률] 비동기 분석 작업 (STT -> 감정 -> 요약) ---
def process_audio_task(diary_id: int):
    db = SessionLocal()
    logger.info(f"Task Start: diary_id={diary_id}")
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary: return

        # 0. 오디오 포맷 변환 (WebM -> Wav)
        audio_path = diary.audio_path
        if audio_path.endswith(".webm"):
            wav_path = audio_path.replace(".webm", ".wav")
            subprocess.run(['ffmpeg', '-y', '-i', audio_path, '-ar', '16000', '-ac', '1', wav_path], check=True)
            audio_path = wav_path

        # 1. STT 실행 (B님)
        transcript = transcribe(audio_path)
        if not transcript:
            diary.status = "FAILED"
            db.commit()
            return
        diary.transcript = transcript

        # 2. 감정 분석 (C님)
        emotion_result = analyze_emotion(diary.transcript)
        diary.emotion_label = emotion_result["label"]
        diary.emotion_score = emotion_result["all_scores"]

        # 3. [성률] 자동 제목 및 요약 생성
        # logger.info("📝 요약 및 제목 생성 중...")
        # diary.title = generate_title(diary.transcript)
        # diary.summary = generate_summary(diary.transcript)

        diary.status = "COMPLETED"
        db.commit()
        logger.info(f"✅ 분석 완료: {diary.emotion_label}")

    except Exception as e:
        logger.error(f"❌ 에러 발생: {e}")
        diary.status = "FAILED"
        db.commit()
    finally:
        db.close()

# --- 일기 생성 및 조회 API ---
@app.post("/diaries")
async def create_diary(
        bg_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        # current_user: User = Depends(get_current_user) # [은수] 인증 연동 시 추가
):
    file_uuid = str(uuid.uuid4())
    save_path = f"{UPLOAD_DIR}/{file_uuid}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_diary = Diary(uuid=file_uuid, audio_path=save_path, status="PENDING")
    # new_diary.user_id = current_user.id # [은수] 인증 연동 시 유저 ID 저장
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)

    bg_tasks.add_task(process_audio_task, new_diary.id)
    return {"message": "Accepted", "id": new_diary.id}

@app.get("/diaries/{diary_id}")
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary: raise HTTPException(status_code=404, detail="Not found")
    return diary

# --- [주영] 피드백 및 통계 API ---
class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)

@app.post("/diaries/{diary_id}/feedback")
def create_diary_feedback(diary_id: int, req: FeedbackRequest, db: Session = Depends(get_db)):
    return create_feedback(db, CreateFeedbackCommand(diary_id=diary_id, rating=req.rating, comment=req.comment))

@app.get("/admin/feedback/stats")
def get_feedback_stats(db: Session = Depends(get_db)):
    """[주영] 피드백 대시보드용 통계 API"""
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0
    feedback_count = db.query(func.count(Feedback.id)).scalar()
    return {
        "average_rating": round(float(avg_rating), 2),
        "total_feedbacks": feedback_count
    }

@app.get("/reports/weekly")
def get_weekly_report(db: Session = Depends(get_db)):
    stats = db.query(Diary.emotion_label, func.count(Diary.id)).filter(Diary.status == "COMPLETED").group_by(Diary.emotion_label).all()
    return {label: count for label, count in stats if label}
