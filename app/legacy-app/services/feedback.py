# from dataclasses import dataclass
# from typing import Optional

# from fastapi import HTTPException
# from sqlalchemy.orm import Session

# from app.legacy.app.models import Diary, Feedback


# @dataclass(frozen=True)
# class CreateFeedbackCommand:
#     diary_id: int
#     rating: int
#     comment: Optional[str]


# @dataclass(frozen=True)
# class CreateFeedbackResult:
#     id: int
#     diary_id: int
#     rating: int
#     comment: Optional[str]


# def create_feedback(db: Session, cmd: CreateFeedbackCommand) -> CreateFeedbackResult:
#     # 1️⃣ rating 검증
#     if not (1 <= cmd.rating <= 5):
#         raise HTTPException(status_code=400, detail="rating must be between 1 and 5")

#     comment = cmd.comment.strip() if cmd.comment else None
#     if comment and len(comment) > 5000:
#         raise HTTPException(status_code=400, detail="comment is too long")

#     # 2️⃣ Diary 존재 확인
#     diary = db.query(Diary).filter(Diary.id == cmd.diary_id).first()
#     if not diary:
#         raise HTTPException(status_code=404, detail="Diary not found")

#     # 3️⃣ 분석 완료 후에만 허용
#     if diary.status not in ("COMPLETED", "READY"):
#         raise HTTPException(
#             status_code=409,
#             detail="Diary analysis is not completed yet",
#         )

#     # 일기당 1회만 허용하고 싶으면 여기서 체크
#     # existing = db.query(Feedback).filter(Feedback.diary_id == cmd.diary_id).first()
#     # if existing:
#     #     raise HTTPException(status_code=409, detail="Feedback already submitted")

#     # 4️⃣ 저장
#     feedback = Feedback(
#         diary_id=cmd.diary_id,
#         rating=cmd.rating,
#         comment=comment,
#     )
#     db.add(feedback)
#     db.commit()
#     db.refresh(feedback)

#     return CreateFeedbackResult(
#         id=feedback.id,
#         diary_id=feedback.diary_id,
#         rating=feedback.rating,
#         comment=feedback.comment,
#     )
