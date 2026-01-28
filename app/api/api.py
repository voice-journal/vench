from fastapi import APIRouter
from app.domains.auth.router import router as auth_router
from app.domains.diary.router import router as diary_router
from app.domains.diary.router import router as feedback_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(diary.router, prefix="/diaries", tags=["Diary"])
api_router.include_router(feedback_router, prefix="/feedbacks", tags=["Feedback"])
