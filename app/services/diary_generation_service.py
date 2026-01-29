# app/services/diary_generation_service.py
import torch
from transformers import pipeline

class DiaryGenerationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # [변경] Gemma-2b(8GB+) -> TinyLlama-1.1B(4GB)로 교체하여 OOM 방지
            model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            print(f"⏳ Loading Gen-AI Model ({model_id})...")

            cls._instance = super().__new__(cls)
            cls.generator = pipeline(
                "text-generation",
                model=model_id,
                device=-1,  # CPU
                torch_dtype=torch.float32,
            )
            print("✅ Model Loaded!")
        return cls._instance

    def generate_diary(self, transcript: str, emotion: str) -> str:
        if not transcript or len(transcript) < 5:
            return "내용이 너무 짧아 일기를 생성할 수 없어요."

        # TinyLlama Chat 템플릿 적용
        # (System Prompt로 페르소나 부여)
        messages = [
            {
                "role": "system",
                "content": "You are a warm-hearted AI diary writer. Write a short, emotional diary entry in Korean based on the user's input."
            },
            {
                "role": "user",
                "content": f"다음 내용을 바탕으로 '{emotion}' 감정이 담긴 따뜻한 한국어 일기를 써줘. 시작은 '오늘은 참'으로 해줘.\n\n내용: {transcript}"
            }
        ]

        # 프롬프트 변환
        prompt = self.generator.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        try:
            results = self.generator(
                prompt,
                max_new_tokens=200, # 생성 길이 제한
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )

            generated_text = results[0]['generated_text']

            # 생성된 텍스트에서 답변 부분만 추출 (<|assistant|> 이후)
            if "<|assistant|>" in generated_text:
                final_diary = generated_text.split("<|assistant|>")[-1].strip()
            else:
                final_diary = generated_text

            # 혹시 영어가 섞여 나올 경우를 대비한 안전장치 (선택 사항)
            return final_diary

        except Exception as e:
            print(f"❌ Diary Generation Error: {e}")
            return f"오늘은 {emotion}을(를) 느낀 하루였다. \"{transcript}\" 라는 일이 있었기 때문이다."

    def generate_title(self, diary_content: str) -> str:
        # 제목 생성 로직 (첫 줄 사용)
        first_line = diary_content.split("\n")[0]
        return first_line[:20] + "..." if len(first_line) > 20 else first_line

# 싱글톤 인스턴스
diary_service = DiaryGenerationService()
