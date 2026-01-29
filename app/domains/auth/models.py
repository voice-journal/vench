from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    diaries = relationship("Diary", back_populates="user", cascade="all, delete-orphan")