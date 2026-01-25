from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db, SessionLocal
from app.models import Diary
import shutil, os, uuid, logging
from app.services.emotion_service import analyze_emotion

# DB 초기화 (테이블 생성)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vench")

app = FastAPI()
Instrumentator().instrument(app).expose(app)

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 비동기 작업: 실제 AI 분석 로직
def process_audio_task(diary_id: int):
    db = SessionLocal()
    logger.info(f"Task Start: diary_id={diary_id}")
    try:
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if diary:
            # 1. STT (아직 STT는 없으니 가짜 텍스트 사용)
            # 나중에 여기에 stt_service(diary.audio_path) 결과를 넣을 예정
            fake_transcript = "오늘 팀원들이랑 서버 에러 잡느라 고생했지만 해결해서 너무 뿌듯하다."
            diary.transcript = fake_transcript

            # 2. 감정 분석 (User님이 만든 AI!) 🔥
            logger.info("🤖 AI 감정 분석 시작...")
            emotion_result = analyze_emotion(diary.transcript)

            # 3. 결과 DB 저장
            diary.emotion_label = emotion_result['label']
            diary.emotion_score = emotion_result['all_scores'] # 전체 점수(JSON) 저장
            diary.status = "COMPLETED"

            db.commit()
            logger.info(f"✅ 분석 완료: {diary.emotion_label}")

    except Exception as e:
        logger.error(f"Error processing diary {diary_id}: {e}")
        # 에러 발생 시 DB에 '실패' 상태로 기록
        try:
            diary_error = db.query(Diary).filter(Diary.id == diary_id).first()
            if diary_error:
                diary_error.status = "FAILED"
                db.commit()
        except:
            pass # DB 연결 에러면 어쩔 수 없음
    finally:
        db.close()

@app.post("/diaries")
async def create_diary(bg_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. 파일 저장
    file_uuid = str(uuid.uuid4())
    save_path = f"{UPLOAD_DIR}/{file_uuid}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. DB 기록
    new_diary = Diary(uuid=file_uuid, audio_path=save_path, status="PENDING")
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)

    # 3. 비동기 큐에 등록 (사용자는 기다리지 않음)
    bg_tasks.add_task(process_audio_task, new_diary.id)

    return {"message": "Accepted", "id": new_diary.id}
