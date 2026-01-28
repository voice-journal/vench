from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.domains.feedback.service import CreateFeedbackCommand, create_feedback


router = APIRouter()

# TODO: DTO 분리해주세요! -> schemas.py
class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)

# TODO: 상태 코드 지정해주세요!
@router.post(
    "/",
    # response_model=FeedbackResponse, 
    # status_code=status.HTTP_201_CREATED,
    summary="피드백 작성"        
)
def create_diary_feedback(
    diary_id: int,
    req: FeedbackRequest,
    db: Session = Depends(get_db),
):
    result = create_feedback(
        db,
        CreateFeedbackCommand(
            diary_id=diary_id,
            rating=req.rating,
            comment=req.comment,
        ),
    )

    return {
        "id": result.id,
        "diary_id": result.diary_id,
        "rating": result.rating,
        "comment": result.comment,
    }