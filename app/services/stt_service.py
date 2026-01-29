# app/services/stt_service.py
import os
from faster_whisper import WhisperModel
from pydub import AudioSegment

# 모델 로딩
model = WhisperModel("small", device="cpu", compute_type="int8")

def convert_to_wav(input_path: str) -> str:
    """
    모든 오디오 포맷을 16kHz Mono WAV로 변환
    """
    try:
        # pydub로 로드 (ffmpeg 자동 사용)
        audio = AudioSegment.from_file(input_path)

        # 경로 설정 (.wav로 변경)
        output_path = os.path.splitext(input_path)[0] + ".wav"

        # 변환 저장 (16000Hz, Mono)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")

        return output_path
    except Exception as e:
        print(f"⚠️ 오디오 변환 실패 (원본 사용): {e}")
        return input_path

def transcribe(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        return ""

    # [New] 포맷 변환 수행
    safe_audio_path = convert_to_wav(audio_path)

    try:
        segments, info = model.transcribe(
            safe_audio_path,
            language="ko",
            vad_filter=True,
            beam_size=5,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()

        if len(transcript) < 2: # 너무 짧은 경우 필터링
            return ""

        return transcript

    except Exception as e:
        print(f"❌ STT 실패: {e}")
        return ""
