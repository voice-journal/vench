import uuid
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.diary.models import Diary
from app.services.diary_task import process_audio_task, UPLOAD_DIR

router = APIRouter()

# TODO: DTO(-> schemas.py), 응답 상태 코드 지정해주세요!
# TODO: 서비스 로직 분리해주세요!
@router.post(
    "/", 
    # response_model=DiaryResponse, 
    # status_code=status.HTTP_201_CREATED,
    summary="음성 일기 업로드 및 분석 시작"
)
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

    bg_tasks.add_task(process_audio_task, new_diary.id) # FIXME: 여기 타입 에러 나요~
    return {"id": new_diary.id}

# TODO: DTO(-> schemas.py), 응답 상태 코드 지정해주세요!
# TODO: 서비스 로직 분리해주세요!
@router.get(
    "/{diary_id}", 
    # response_model=DiaryResponse,
    summary="일기 상세 조회"
)
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary: raise HTTPException(status_code=404)
    return diary
