import logging
import logging.config

from fastapi import FastAPI
from fastapi import Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.api import api_router
from app.core.database import Base, engine
from app.core.exceptions import BusinessException
from app.core.config import settings

from app.domains.auth import models as auth_models
from app.domains.diary import models as diary_models
from app.domains.feedback import models as feedback_models

# ==========================================
# 1. 로깅 설정 로드 (Logging Setup)
# ==========================================
try:
    # app/core/logging.py가 있으면 해당 설정을 따름
    from app.core.logging import LOGGING_CONFIG
    logging.config.dictConfig(LOGGING_CONFIG)
except ImportError:
    # 설정 파일이 없으면 기본 설정 사용
    logging.basicConfig(level=logging.INFO)

# "Vench" 로거를 가져와야 설정(logging.py)이 적용된 포맷으로 출력됩니다.
logger = logging.getLogger("Vench")


# ==========================================
# 2. Lifespan (앱 수명 주기 관리)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Start] 서버 시작 시 실행
    
    # 1. 설정 로그 출력
    logger.info("🚀 Vench Backend Server is starting up...")

    # 2. DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    yield # 앱 실행 중
    
    # [Shutdown] 서버 종료 시 실행
    logger.info("👋 Vench Backend Server is shutting down...")

# ==========================================
# 3. 애플리케이션 초기화
# ==========================================
# DB 테이블 자동 생성 (실무에서는 Alembic 마이그레이션 권장)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vench API", lifespan=lifespan)

# Prometheus 모니터링 엔드포인트 노출 (/metrics)
Instrumentator().instrument(app).expose(app)

# ==========================================
# 4. 전역 예외 핸들러 (Global Exception Handler)
# ==========================================
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):    
    if exc.log_message:
        # 개발자가 디버깅을 위해 남긴 상세 메시지 기록
        logger.error(f"[BusinessError] {exc.code} - {exc.log_message}")
    else:
        logger.warning(f"[BusinessError] {exc.code} - {exc.message}")
    
    # 클라이언트(프론트엔드)에게는 약속된 JSON 포맷만 전달
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
        }
    )

# ==========================================
# 5. 라우터 등록
# ==========================================
app.include_router(api_router)