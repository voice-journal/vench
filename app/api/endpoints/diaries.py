import uuid, shutil, os
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Diary
from app.services.diary_task import process_audio_task, UPLOAD_DIR

router = APIRouter()

@router.post("/")
async def create_diary(
        bg_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    file_uuid = str(uuid.uuid4())
    save_path = f"{UPLOAD_DIR}/{file_uuid}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_diary = Diary(uuid=file_uuid, audio_path=save_path, status="PENDING")
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)

    bg_tasks.add_task(process_audio_task, new_diary.id)
    return {"id": new_diary.id}

@router.get("/{diary_id}")
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary: raise HTTPException(status_code=404)
    return diary
