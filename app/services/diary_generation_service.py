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
                temperature=0.7,
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

    def generate_advice(self, transcript: str, emotion_label: str) -> str:
        """[New] 사용자 감정과 내용을 바탕으로 따뜻한 위로 메시지 생성"""
        if not transcript: return "오늘 하루도 수고 많으셨어요."

        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 공감 능력이 뛰어난 '전문 심리 상담사'입니다. "
                    "사용자의 이야기와 감정을 듣고 따뜻한 위로와 격려의 말을 건네주세요.\n"
                    "규칙:\n"
                    "1. 말투: '~해요', '~네요' 등 부드럽고 친절한 존댓말을 사용하세요.\n"
                    "2. 길이: 3문장 이내로 간결하지만 진심이 느껴지게 작성하세요.\n"
                    "3. 내용: 사용자의 감정(기쁨/슬픔/분노 등)을 인정해주고, 긍정적인 메시지로 마무리하세요."
                )
            },
            {
                "role": "user",
                "content": (
                    f"사용자 감정: {emotion_label}\n"
                    f"사용자 이야기: \"{transcript}\"\n\n"
                    "위 내용에 대해 따뜻한 위로의 말을 해줘."
                )
            }
        ]

        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=150,  # 짧고 굵게
                temperature=0.7, # 감성적인 답변을 위해 약간 높게
            )
            advice = response["choices"][0]["message"]["content"]

            # 후처리
            advice = re.sub(r'[\u4e00-\u9fff]+', '', advice)
            advice = advice.replace("[|assistant|]", "").strip()

            return advice

        except Exception as e:
            print(f"❌ Advice Generation Error: {e}")
            return "당신의 이야기를 들어줄 수 있어 기뻐요. 내일은 더 좋은 하루가 될 거예요."

# 싱글톤 인스턴스
diary_service = DiaryGenerationService()
