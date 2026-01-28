from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.api import api_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vench API")
Instrumentator().instrument(app).expose(app)

app.include_router(api_router)
# process_audio_task는 diary_task.py로 이동 완료
