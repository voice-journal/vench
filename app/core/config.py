import os
import logging
from pprint import pformat
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정 (보통 main.py 상단에 위치)
# TODO: main으로 이동
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("[Config]")

class Settings:
    
    """
    Spring의 @ConfigurationProperties처럼
    환경 변수와 설정값을 관리하는 클래스입니다.
    """
    # 1. 프로젝트 기본 설정
    PROJECT_NAME: str = "Vench"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"  # API 버전 관리용

    # 2. 보안 (Security) - JWT & Password
    # 🚨 주의: 배포 시에는 반드시 .env에서 변경해야 함
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "vench-hackathon-secret-key-2024")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1일 (해커톤용)

    # 3. 데이터베이스 (Database)
    # .env 파일의 DATABASE_URL이 없으면 로컬 기본값 사용
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://user:password@localhost:3306/vench?charset=utf8mb4"
    )

    # 4. 백엔드/프론트엔드 연동 URL
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # 5. CORS 설정 (프론트엔드 도메인 허용)
    # 실제 운영 환경에서는 구체적인 도메인 리스트로 제한 필요
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8501", # Streamlit 기본 포트
        "http://localhost:3000", # Grafana 등
        "*",                     # 개발 편의상 전체 허용 (주의)
    ]

    def to_dict(self):
        """
        클래스의 속성들을 딕셔너리로 변환 (Masking 처리를 위해 분리)
        """
        return {
            k: getattr(self, k) 
            for k in dir(self) 
            if not k.startswith("__") and not callable(getattr(self, k))
        }

    def __str__(self):
        """
        객체를 문자열로 출력할 때 호출
        """
        data = self.to_dict()
        
        # 🔒 보안: 비밀번호나 키는 로그에 남지 않게 마스킹 처리
        if "SECRET_KEY" in data:
            data["SECRET_KEY"] = "****" 
        if "DATABASE_URL" in data:
            # DB URL도 패스워드 부분 마스킹 권장 (간단히 처리)
            data["DATABASE_URL"] = data["DATABASE_URL"].split("@")[-1] if "@" in data["DATABASE_URL"] else data["DATABASE_URL"]

        # 예쁘게 포맷팅 (들여쓰기 4칸)
        return pformat(data, indent=4, width=80)

# Singleton 인스턴스 생성
# (Spring의 Bean처럼 어디서든 settings.SECRET_KEY로 접근 가능)
settings = Settings()

if __name__ == "__main__":
    logger.info("🚀 Project Settings Loaded:\n" + str(settings))