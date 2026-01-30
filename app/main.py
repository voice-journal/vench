import logging
import logging.config
import asyncio # [New] 비동기 루프용

from fastapi import FastAPI
from fastapi import Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.api import api_router
from app.core.database import Base, engine, SessionLocal # [New] SessionLocal 추가
from app.core.exceptions import BusinessException
from app.core.config import settings

# [New] 모니터링 서비스 임포트
from app.services.monitoring_service import update_business_metrics

from app.domains.auth import models as auth_models
from app.domains.diary import models as diary_models
from app.domains.feedback import models as feedback_models

# ==========================================
# 1. 로깅 설정 로드
# ==========================================
try:
    from app.core.logging import LOGGING_CONFIG
    logging.config.dictConfig(LOGGING_CONFIG)
except ImportError:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Vench")

# ==========================================
# [New] 백그라운드 메트릭 업데이트 태스크
# ==========================================
async def periodic_metrics_update():
    """15초마다 비즈니스 지표를 DB에서 조회하여 갱신"""
    while True:
        try:
            # 별도의 DB 세션을 열어서 사용
            with SessionLocal() as db:
                update_business_metrics(db)
        except Exception as e:
            logger.error(f"Metric update loop error: {e}")

        await asyncio.sleep(15) # 15초 대기

# ==========================================
# 2. Lifespan (앱 수명 주기 관리)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Start] 서버 시작 시 실행
    logger.info("🚀 Vench Backend Server is starting up...")
    Base.metadata.create_all(bind=engine)

    # [New] 메트릭 업데이트 백그라운드 태스크 시작
    metrics_task = asyncio.create_task(periodic_metrics_update())

    yield # 앱 실행 중

    # [Shutdown] 서버 종료 시 실행
    # 태스크 취소
    metrics_task.cancel()
    logger.info("👋 Vench Backend Server is shutting down...")

# ==========================================
# 3. 애플리케이션 초기화
# ==========================================
app = FastAPI(title="Vench API", lifespan=lifespan)

# Prometheus 모니터링 엔드포인트 노출 (/metrics)
Instrumentator().instrument(app).expose(app)

# ==========================================
# 4. 전역 예외 핸들러
# ==========================================
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    if exc.log_message:
        logger.error(f"[BusinessError] {exc.code} - {exc.log_message}")
    else:
        logger.warning(f"[BusinessError] {exc.code} - {exc.message}")

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
