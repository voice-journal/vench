# app/domains/diary/schemas.py
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel

class DiaryCreateResponse(BaseModel):
    id: int
    message: str = "일기 분석 요청이 접수되었습니다."

class DiaryResponse(BaseModel):
    id: int
    uuid: str
    status: str            # PENDING, PROCESSING, COMPLETED, FAILED

    # 분석 결과
    title: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None       # 재생성된 일기 내용
    emotion_label: Optional[str] = None
    emotion_score: Optional[Any] = None # JSON 데이터

    created_at: datetime

    class Config:
        from_attributes = True
