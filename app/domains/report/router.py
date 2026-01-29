from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.report import service, schemas

router = APIRouter()

@router.get(
    "/weekly",
    summary="주간 감정 통계 조회"
)
def get_weekly_report(db: Session = Depends(get_db)):
    data = service.get_weekly_emotion_stats(db)
    return data
