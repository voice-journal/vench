from typing import Optional
from fastapi import status

class BusinessException(Exception):
    """
    비즈니스 로직 에러의 최상위 클래스입니다.
    Spring의 RuntimeException을 상속받아 커스텀 예외를 만드는 것과 유사합니다.
    """
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        log_message: Optional[str] = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.log_message = log_message # 서버 로그용 상세 메시지 (옵션)
        super().__init__(message)

# ==========================================
# 🔐 인증 (Auth) 도메인 예외
# ==========================================
class EmailDuplicateException(BusinessException):
    def __init__(self, email: str = ""):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="AUTH_EMAIL_DUPLICATED",
            message="이미 가입된 이메일입니다.",
            log_message=f"Duplicate email join attempt: {email}"
        )

class UserNotFoundException(BusinessException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="AUTH_USER_NOT_FOUND",
            message="사용자를 찾을 수 없습니다."
        )

class InvalidPasswordException(BusinessException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID_PASSWORD",
            message="이메일 또는 비밀번호가 잘못되었습니다."
        )

class InvalidTokenException(BusinessException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID_TOKEN",
            message="유효하지 않거나 만료된 토큰입니다."
        )

# ==========================================
# 📖 일기 (Diary) 도메인 예외
# ==========================================
class DiaryNotFoundException(BusinessException):
    def __init__(self, diary_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="DIARY_NOT_FOUND",
            message="해당 일기를 찾을 수 없습니다.",
            log_message=f"Diary ID {diary_id} not found"
        )

class AnalysisNotCompletedException(BusinessException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="DIARY_ANALYSIS_NOT_READY",
            message="아직 분석이 완료되지 않았습니다."
        )

class AnalysisFailedException(BusinessException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DIARY_ANALYSIS_FAILED",
            message="AI 분석 중 오류가 발생했습니다."
        )