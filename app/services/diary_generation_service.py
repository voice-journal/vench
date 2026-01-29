import torch
from transformers import pipeline

class DiaryGenerationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("⏳ Loading Gen-AI Model (Gemma-2b)...")
            cls._instance = super().__new__(cls)
            # 로컬 메모리 최적화를 위해 bfloat16 또는 float32 사용
            # M4 Pro는 MPS(Metal Performance Shaders) 사용 가능 시 "mps" 로 설정 추천하지만
            # Docker 환경 호환성을 위해 우선 "cpu" + "float32" 로 안전하게 설정
            cls.generator = pipeline(
                "text-generation",
                model="beomi/gemma-ko-2b",
                device=-1,  # CPU
                torch_dtype=torch.float32,
            )
            print("✅ Model Loaded!")
        return cls._instance

    def generate_diary(self, transcript: str, emotion: str) -> str:
        """
        STT 결과와 감정을 입력받아, 따뜻한 일기체로 재생성
        """
        if not transcript or len(transcript) < 5:
            return "내용이 너무 짧아 일기를 생성할 수 없어요."

        # 프롬프트 엔지니어링
        prompt = (
            f"사용자의 말: \"{transcript}\"\n"
            f"감정: {emotion}\n\n"
            "위 내용을 바탕으로 오늘 하루를 회고하는 따뜻한 일기를 써줘:\n"
            "오늘은 참"
        )

        try:
            # 생성 파라미터 튜닝
            results = self.generator(
                prompt,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2
            )

            generated_text = results[0]['generated_text']

            # 프롬프트 뒷부분(생성된 내용)만 추출 + 시작 문구 복구
            final_diary = "오늘은 참" + generated_text.split("오늘은 참")[-1]
            return final_diary.strip()

        except Exception as e:
            print(f"❌ Diary Generation Error: {e}")
            # 실패 시 Fallback: 룰 기반 간단 변환
            return f"오늘은 {emotion}을(를) 느낀 하루였다. \"{transcript}\" 라는 일이 있었기 때문이다."

    def generate_title(self, diary_content: str) -> str:
        """일기 내용의 첫 문장이나 키워드로 제목 생성"""
        return diary_content[:20] + "..." if len(diary_content) > 20 else diary_content

# 싱글톤 인스턴스
diary_service = DiaryGenerationService()
