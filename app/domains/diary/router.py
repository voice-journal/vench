# app/domains/diary/router.py
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.diary import schemas, service

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.DiaryCreateResponse,
    status_code=202,
    summary="음성 일기 업로드 및 분석 요청"
)
async def create_diary(
        bg_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    new_diary = service.create_new_diary(db, file, bg_tasks)
    return {"id": new_diary.id, "message": "분석이 시작되었습니다."}

@router.get(
    "/{diary_id}",
    response_model=schemas.DiaryResponse,
    summary="일기 상세 조회"
)
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    return service.get_diary_by_id(db, diary_id)
