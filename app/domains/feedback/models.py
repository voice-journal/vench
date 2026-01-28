from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    diary_id = Column(
        Integer,
        ForeignKey("diaries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating = Column(Integer, nullable=False)   # 1~5
    comment = Column(Text, nullable=True)

    diary = relationship("Diary", back_populates="feedbacks")

# FIXME: diary와의 연관관계가 있어야 하는지 재고해주시면 좋겠습니다!