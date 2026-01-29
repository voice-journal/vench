from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 설정 파일에서 settings 가져오기 (환경변수 관리 일원화)
from app.core.config import settings

# 2. 엔진 생성
engine = create_engine(settings.DATABASE_URL)

# 3. 세션 팩토리 생성 (Transaction Scope 관리)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. ORM 모델들이 상속받을 Base 클래스
Base = declarative_base()


def get_db():
    """
    FastAPI의 Depends(get_db)로 주입되어
    요청(Request)마다 DB 세션을 생성하고, 요청이 끝나면 자동으로 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
