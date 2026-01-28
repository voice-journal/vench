from fastapi import APIRouter
from app.api.endpoints import auth, diaries, admin

api_router = APIRouter()

# 도메인별로 경로(Prefix)와 태그를 지정하여 분리
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(diaries.router, prefix="/diaries", tags=["diaries"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
