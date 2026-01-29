# app/domains/diary/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class DiaryCreate(BaseModel):
    pass

class DiaryCreateResponse(BaseModel):
    id: int

class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    emotion_label: Optional[str] = None
    emotion_score: Optional[str] = None
    status: Optional[str] = None

class DiaryResponse(BaseModel):
    id: int
    uuid: str
    audio_path: str
    title: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    emotion_label: Optional[str] = None

    # DB의 JSON 문자열을 유연하게 처리
    emotion_score: Optional[Any] = None

    status: str
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DiaryListResponse(BaseModel):
    items: List[DiaryResponse]
    total: int
