# app/domains/diary/service.py
import shutil
import uuid
import os
from fastapi import UploadFile, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.domains.diary.models import Diary
from app.services.diary_task import process_audio_task

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_new_diary(db: Session, file: UploadFile, bg_tasks: BackgroundTasks) -> Diary:
    # 1. 파일 저장
    file_uuid = str(uuid.uuid4())
    # 확장자 추출 (없으면 .wav 기본값)
    ext = os.path.splitext(file.filename)[1] or ".wav"
    save_path = os.path.join(UPLOAD_DIR, f"{file_uuid}{ext}")

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # 2. DB 저장
    new_diary = Diary(
        uuid=file_uuid,
        audio_path=save_path,
        status="PENDING"
    )
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)

    # 3. 백그라운드 태스크 요청
    bg_tasks.add_task(process_audio_task, new_diary.id)

    return new_diary

def get_diary_by_id(db: Session, diary_id: int) -> Diary:
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    return diary

def get_all_diaries(db: Session, skip: int = 0, limit: int = 10):
    query = db.query(Diary).filter(Diary.status == "COMPLETED")
    total = query.count()

    # 최신순 정렬 (내림차순)
    items = query.order_by(desc(Diary.created_at)).offset(skip).limit(limit).all()

    return {"items": items, "total": total}
