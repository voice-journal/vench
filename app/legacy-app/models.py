# from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from app.database import Base

# class User(Base):
#     """[은수] 사용자 인증을 위한 테이블"""
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, index=True, nullable=False)
#     hashed_password = Column(String(255), nullable=False)
#     full_name = Column(String(100), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     # 관계 설정: 유저는 여러 일기를 가질 수 있음
#     diaries = relationship("Diary", back_populates="user", cascade="all, delete-orphan")

# class Diary(Base):
#     """일기 및 AI 분석 결과 저장 테이블"""
#     __tablename__ = "diaries"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # [은수] 유저 연결
#     uuid = Column(String(36), unique=True, index=True)
#     audio_path = Column(String(255), nullable=False)

#     # [성률] 자동 일기 생성 관련 컬럼
#     title = Column(String(255), nullable=True)
#     transcript = Column(Text, nullable=True)
#     summary = Column(Text, nullable=True)

#     emotion_label = Column(String(50), index=True, nullable=True)
#     emotion_score = Column(JSON, nullable=True)
#     status = Column(String(20), default="PENDING", index=True) # PENDING, PROCESSING, COMPLETED, FAILED
#     model_version = Column(String(50), default="v1.0")
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

#     # 관계 설정
#     user = relationship("User", back_populates="diaries")
#     feedbacks = relationship(
#         "Feedback",
#         back_populates="diary",
#         cascade="all, delete-orphan",
#     )

# class Feedback(Base):
#     """[주영] 사용자 피드백 저장 테이블"""
#     __tablename__ = "feedbacks"

#     id = Column(Integer, primary_key=True)
#     diary_id = Column(
#         Integer,
#         ForeignKey("diaries.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     rating = Column(Integer, nullable=False)   # 1~5
#     comment = Column(Text, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

#     # 관계 설정
#     diary = relationship("Diary", back_populates="feedbacks")
