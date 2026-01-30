# app/services/stt_service.py
import os
from faster_whisper import WhisperModel
from pydub import AudioSegment, effects

# ==========================================
# 1. 모델 업그레이드 (small -> medium)
# ==========================================
# 정확도를 위해 'medium' 모델을 사용합니다.
model = WhisperModel("medium", device="cpu", compute_type="int8")

def convert_to_wav_and_boost(input_path: str) -> str:
    """
    오디오 포맷 변환 및 볼륨 정규화(증폭) 수행
    """
    try:
        # pydub로 로드
        audio = AudioSegment.from_file(input_path)

        # [New] 볼륨 정규화 (Normalization)
        # 소리가 작게 녹음된 경우 최대 볼륨으로 증폭시킵니다.
        audio = effects.normalize(audio)

        # 경로 설정 (.wav로 변경)
        output_path = os.path.splitext(input_path)[0] + ".wav"

        # 변환 저장 (16000Hz, Mono - Whisper 권장 사양)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")

        return output_path
    except Exception as e:
        print(f"⚠️ 오디오 변환/증폭 실패 (원본 사용): {e}")
        return input_path

def transcribe(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        return ""

    # [Updated] 변환 및 볼륨 부스팅 적용
    safe_audio_path = convert_to_wav_and_boost(audio_path)

    try:
        # Transcribe 옵션 튜닝
        segments, info = model.transcribe(
            safe_audio_path,
            language="ko",
            beam_size=5,        # 탐색 너비 (정확도 vs 속도)
            vad_filter=True,    # 무음 구간 필터링
            condition_on_previous_text=False, # 환각(반복) 방지
            # min_silence_duration_ms 인자 제거 (기본값 사용)
        )

        transcript = " ".join(segment.text.strip() for segment in segments).strip()

        if len(transcript) < 2:
            return ""

        return transcript

    except Exception as e:
        print(f"❌ STT 실패: {e}")
        return ""
