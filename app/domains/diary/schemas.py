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
    advice: Optional[str] = None
    process_message: Optional[str] = None # [New]
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
    advice: Optional[str] = None

    # [New] 프론트엔드로 진행 상황 텍스트 전달
    process_message: Optional[str] = None

    emotion_label: Optional[str] = None
    emotion_score: Optional[Any] = None
    status: str
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DiaryListResponse(BaseModel):
    items: List[DiaryResponse]
    total: int
