import os

# 로그 레벨 설정 (기본값 INFO)
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # FastAPI 기본 로거
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # 우리 프로젝트 전용 로거
        "Vench": {
            "handlers": ["console"],  # 파일 없이 콘솔만 사용
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}