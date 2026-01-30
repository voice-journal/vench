import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.domains.auth.models import User, UserRole
from app.core.security import get_password_hash

logger = logging.getLogger("Vench")

def init_data():
    """앱 시작 시 관리자와 테스트 유저가 없으면 생성합니다."""
    db: Session = SessionLocal()
    try:
        # 1. 관리자 계정 (admin@vench.com / 1234)
        admin = db.query(User).filter(User.email == "admin@vench.com").first()
        if not admin:
            logger.info("🛠️ Creating initial Admin user...")
            db.add(User(
                email="admin@vench.com",
                password=get_password_hash("12341234"),
                nickname="Admin",
                role=UserRole.ADMIN
            ))
            
        # 2. 테스트 일반 유저 (user@vench.com / 1234)
        user = db.query(User).filter(User.email == "user@vench.com").first()
        if not user:
            logger.info("🛠️ Creating initial Test user...")
            db.add(User(
                email="user@vench.com",
                password=get_password_hash("12341234"),
                nickname="Test User",
                role=UserRole.USER
            ))
            
        db.commit()
        logger.info("✅ Initial data seeding completed!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize data: {e}")
        db.rollback()
    finally:
        db.close()