import logging
import logging.config
import asyncio
from contextlib import asynccontextmanager # [수정] 누락된 임포트 추가 및 정리

from fastapi import FastAPI
from fastapi import Request
# from fastapi.concurrency import asynccontextmanager # [삭제] 표준 라이브러리 사용 권장
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.api import api_router
from app.core.database import Base, engine, SessionLocal
from app.core.exceptions import BusinessException
from app.core.config import settings
from app.core.init_data import init_data

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
# 백그라운드 메트릭 업데이트 태스크
# ==========================================
async def periodic_metrics_update():
    """15초마다 비즈니스 지표를 DB에서 조회하여 갱신"""
    while True:
        try:
            with SessionLocal() as db:
                update_business_metrics(db)
            # logger.info("✅ Metrics Updated") # 디버깅용 (필요시 주석 해제)
        except Exception as e:
            logger.error(f"Metric update loop error: {e}")

        await asyncio.sleep(15)

# ==========================================
# 2. Lifespan (앱 수명 주기 관리)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Start] 서버 시작 시 실행
    logger.info("🚀 Vench Backend Server is starting up...")

    # 1. DB 테이블 생성 (테이블이 없을 때만 생성됨)
    Base.metadata.create_all(bind=engine)

    # 2. 초기 데이터 주입
    init_data()

    # 3. [Fix] 메트릭 업데이트 태스크 시작 (yield 이전에 실행해야 함!)
    metrics_task = asyncio.create_task(periodic_metrics_update())
    logger.info("📈 Background metrics task started.")

    yield # 🟢 앱 실행 중 (여기서 대기)

    # [Shutdown] 서버 종료 시 실행
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass

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
