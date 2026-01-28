import logging, os
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.api import api_router # 통합 라우터 임포트
from app.database import Base, engine

# DB 초기화
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vench API")
Instrumentator().instrument(app).expose(app)

# 핵심: 모든 API를 통합 라우터를 통해 등록
app.include_router(api_router)

UPLOAD_DIR = "data/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 비동기 작업 로직은 공통으로 유지하거나 서비스 레이어로 추후 이전 가능
def process_audio_task(diary_id: int):
    # ... (기존 비동기 로직 유지)
    pass
