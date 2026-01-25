import logging

logger = logging.getLogger("vench")

def transcribe(audio_path: str) -> str:
    """
    audio_path(파일 경로)를 받아 STT 텍스트를 반환한다.
    - 지금은 stub (B가 faster-whisper 구현을 여기로 연결)
    - 실패하면 빈 문자열 반환(파이프라인이 죽지 않게)
    """
    try:
        # TODO: B가 실제 STT 구현 시 여기서 호출
        return ""
    except Exception as e:
        logger.exception(f"STT transcribe failed: audio_path={audio_path}, err={e}")
        return ""
