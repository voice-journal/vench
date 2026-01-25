"""
faster-whisper 모델 로딩 및 최적화
        •	녹음 파일(webm / wav) → 텍스트 변환
        •	transcribe(audio_path) → transcript 함수 제공
        •	짧은 음성 / 인식 실패 케이스 처리

⚠️ 놓치기 쉬운 포인트 (보완점):
        1	오디오 포맷 지옥 (WebM vs Wav): Streamlit이나 브라우저 녹음은 주로 webm 포맷으로 들어옵니다. Whisper는 wav를 좋아합니다. FFmpeg로 webm → wav 변환하는 코드를 B가 무조건 짜야 합니다.
        2	빈 오디오 처리: 사용자가 버튼만 누르고 아무 말도 안 했을 때, Whisper가 환각(Hallucination)을 보거나 에러가 날 수 있습니다. "텍스트 길이가 0이면 에러 처리"하는 로직이 필요합니다.
"""

import os

from faster_whisper import WhisperModel

# 1. 모델 전역 로딩 (중요)
# size: tiny / base / small / medium
# 해커톤 추천: small (속도/정확도 균형)
model = WhisperModel(
    "small",
    device="cpu",  # GPU 없으면 "cpu"
    compute_type="int8",  # CPU면 "int8"
)


def transcribe(audio_path: str) -> str:
    """
    음성 파일 경로를 받아 텍스트로 변환
    실패 시 빈 문자열 반환
    """
    if not os.path.exists(audio_path):
        print("❌ 음성 파일 없음")
        return ""

    try:
        segments, info = model.transcribe(
            audio_path,
            language="ko",
            vad_filter=True,  # 무음 구간 제거
            beam_size=5,
        )

        # 결과 합치기
        transcript = " ".join(segment.text.strip() for segment in segments)
        transcript = transcript.strip()

        # 너무 짧은 음성 처리
        if len(transcript) < 5:
            print("⚠️ 음성이 너무 짧음")
            return ""

        return transcript

    except Exception as e:
        print(f"❌ STT 실패: {e}")
        return ""
