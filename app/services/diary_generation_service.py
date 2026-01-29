# app/services/diary_generation_service.py
import os
import re
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class DiaryGenerationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # 모델 로딩 (기존과 동일)
            print("⏳ Downloading LG EXAONE 3.0 7.8B (GGUF Quantized)...")
            model_path = hf_hub_download(
                repo_id="mradermacher/EXAONE-3.0-7.8B-Instruct-GGUF",
                filename="EXAONE-3.0-7.8B-Instruct.Q4_K_M.gguf",
                cache_dir="./data/models"
            )
            print(f"✅ Downloaded to: {model_path}")

            cls._instance = super().__new__(cls)
            cls.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_gpu_layers=0,
                verbose=False
            )
            print("✅ LG EXAONE Model Loaded!")
        return cls._instance

    def generate_diary(self, transcript: str, emotion: str) -> str:
        """일기 내용 본문 생성"""
        if not transcript or len(transcript) < 10:
            return transcript

        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 '감성 일기 에디터'입니다. 사용자의 말을 다듬어 일기 본문을 작성하세요.\n"
                    "1. [사실 기반]: 없는 내용은 절대 지어내지 마세요.\n"
                    "2. [문체]: '~했다', '~였다' 등 차분한 독백체로 작성하세요.\n"
                    "3. [형식]: 제목을 쓰지 말고, 바로 본문 내용만 작성하세요."
                )
            },
            {
                "role": "user",
                "content": f"원문: \"{transcript}\"\n\n위 내용을 차분한 일기 본문으로 다듬어줘."
            }
        ]

        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=400,
                temperature=0.3,
                top_p=0.9
            )
            generated_text = response["choices"][0]["message"]["content"]

            # 후처리
            final_diary = re.sub(r'[\u4e00-\u9fff]+', '', generated_text)
            final_diary = final_diary.replace("()", "").replace("[|assistant|]", "").strip()
            return final_diary

        except Exception as e:
            print(f"❌ Diary Body Error: {e}")
            return transcript

    def generate_title(self, diary_content: str) -> str:
        """[New] 일기 내용을 읽고 '감성 제목'을 별도로 생성"""
        if not diary_content: return "오늘의 기록"

        # 제목 생성을 위한 전용 프롬프트
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 '일기 제목 작가'입니다. 주어진 일기 내용을 읽고 가장 어울리는 제목을 지어주세요.\n"
                    "규칙:\n"
                    "1. 내용을 함축하는 **감성적이고 은유적인 제목**을 지으세요.\n"
                    "2. 길이는 **공백 포함 20자 이내**로 짧게 하세요.\n"
                    "3. 따옴표나 '제목:' 같은 접두사를 붙이지 말고 오직 제목 텍스트만 출력하세요."
                )
            },
            {
                "role": "user",
                "content": f"일기 내용: \"{diary_content}\"\n\n이 일기에 어울리는 짧고 멋진 제목 하나만 지어줘."
            }
        ]

        try:
            # 제목은 짧으니까 max_tokens를 작게 설정 (속도 최적화)
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=50,
                temperature=0.7, # 제목은 약간 창의적이어도 됨 (0.3 -> 0.7)
            )
            title = response["choices"][0]["message"]["content"]

            # 후처리 (따옴표, 특수문자 제거)
            title = title.replace('"', '').replace("'", "").replace(".", "").strip()
            title = re.sub(r'[\u4e00-\u9fff]+', '', title) # 한자 제거

            # 혹시 모를 긴 설명 방지
            if "\n" in title: title = title.split("\n")[0]

            return title

        except Exception as e:
            print(f"❌ Title Generation Error: {e}")
            # 실패 시 기존 방식(첫 문장)으로 백업
            return diary_content.split("\n")[0][:20] + "..."

# 싱글톤 인스턴스
diary_service = DiaryGenerationService()
