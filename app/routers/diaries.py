from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import os
import uuid

from app.database import get_db
from app.models import Diary
from app.services.diary_service import schedule_pipeline

router = APIRouter(prefix="/diaries", tags=["diaries"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/storage/uploads")  # docker에서는 이 경로를 volume으로 잡는 게 보통

@router.post("")
def create_diary(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1) 파일 저장
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    diary_uuid = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{diary_uuid}.webm")

    with open(save_path, "wb") as f:
        f.write(file.file.read())

    # 2) DB row 생성 (PROCESSING 시작)
    diary = Diary(
        uuid=diary_uuid,
        audio_path=save_path,
        status="PROCESSING",
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)

    # 3) 백그라운드 파이프라인 등록
    schedule_pipeline(background_tasks, db, diary_id=diary.id)

    return {"id": diary.id, "uuid": diary.uuid, "status": diary.status}


@router.get("/{diary_id}")
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    return {
        "id": diary.id,
        "uuid": diary.uuid,
        "status": diary.status,
        "audio_path": diary.audio_path,
        "transcript": diary.transcript,
        "emotion_label": diary.emotion_label,
        "emotion_score": diary.emotion_score,
        "error_message": diary.error_message,
        "created_at": diary.created_at,
    }
