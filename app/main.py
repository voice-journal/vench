from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db, SessionLocal
from app.models import Diary
import shutil, os, uuid, logging

# DB 초기화 (테이블 생성)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vench")

app = FastAPI()
Instrumentator().instrument(app).expose(app)

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 비동기 작업 (나중에 팀원들이 로직을 채울 곳)
def process_audio_task(diary_id: int):
    db = SessionLocal()
    logger.info(f"Task Start: diary_id={diary_id}")
    try:
        # TODO: 여기서 STT, NLP 함수를 호출하게 됩니다.
        # 지금은 임시로 '성공' 처리만 해둡니다.
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if diary:
            diary.status = "COMPLETED"
            diary.transcript = "아직 AI 모듈 연결 전입니다."
            db.commit()
    except Exception as e:
        logger.error(f"Error: {e}")
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
