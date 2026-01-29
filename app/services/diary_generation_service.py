# app/services/diary_generation_service.py
import os
import re
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class DiaryGenerationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("⏳ Downloading LG EXAONE 3.0 7.8B (GGUF Quantized)...")

            # 1. GGUF 모델 파일 다운로드 (최초 1회만 실행됨)
            # 7.8B 모델을 4비트로 압축하여 약 5GB 정도의 메모리만 사용합니다.
            model_path = hf_hub_download(
                repo_id="mradermacher/EXAONE-3.0-7.8B-Instruct-GGUF",
                filename="EXAONE-3.0-7.8B-Instruct.Q4_K_M.gguf",
                cache_dir="./data/models"  # 모델 저장 위치
            )

            print(f"✅ Downloaded to: {model_path}")
            print("⏳ Loading Llama CPP Engine...")

            cls._instance = super().__new__(cls)

            # 2. 엔진 초기화 (CPU 모드)
            # n_ctx=4096: 긴 문맥 처리를 위한 설정
            cls.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_gpu_layers=0, # Docker(CPU) 환경이므로 0
                verbose=False
            )
            print("✅ LG EXAONE Model Loaded!")
        return cls._instance

    def generate_diary(self, transcript: str, emotion: str) -> str:
        if not transcript or len(transcript) < 10:
            return transcript

        # 3. LG EXAONE Chat Template 구조에 맞춘 메시지 구성
        # EXAONE은 한국어 지시 사항을 매우 잘 이해합니다.
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 사용자의 하루를 따뜻하게 기록해주는 '감성 일기 에디터'입니다. "
                    "아래 원칙을 엄격히 지켜주세요:\n"
                    "1. [사실 준수]: 사용자가 언급하지 않은 내용(날씨, 음식 등)은 절대 지어내지 마세요.\n"
                    "2. [문체 변환]: 구어체(말투)를 '오늘 나는 ~했다' 형태의 차분한 문어체 일기로 다듬으세요.\n"
                    "3. [형식]: 한자나 괄호 설명을 쓰지 말고, 오직 자연스러운 한국어로만 작성하세요."
                )
            },
            {
                "role": "user",
                "content": f"원문: \"{transcript}\"\n\n위 원문의 사실관계만 유지하면서 문장을 매끄러운 일기로 다듬어주세요."
            }
        ]

        try:
            # 4. 추론 (Inference)
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=400,
                temperature=0.3,  # 사실 유지력 강화
                top_p=0.9,
                repeat_penalty=1.2
            )

            generated_text = response["choices"][0]["message"]["content"]

            # 5. 후처리 (한자 및 잡음 제거)
            final_diary = re.sub(r'[\u4e00-\u9fff]+', '', generated_text)
            final_diary = final_diary.replace("()", "").strip()

            # 혹시 모를 태그 제거 ([|assistant|] 등)
            final_diary = final_diary.replace("[|assistant|]", "").strip()

            return final_diary

        except Exception as e:
            print(f"❌ Diary Generation Error: {e}")
            return transcript

    def generate_title(self, diary_content: str) -> str:
        lines = diary_content.split("\n")
        if not lines: return "오늘의 기록"

        title = lines[0].replace(".", "").strip()
        title = re.sub(r'[\u4e00-\u9fff]+', '', title)
        return title[:20] + "..." if len(title) > 20 else title

# 싱글톤 인스턴스
diary_service = DiaryGenerationService()
