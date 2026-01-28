# app/services/summary_service.py
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

# M4 Pro의 성능을 활용하기 위해 KoBART 모델 사용
model_name = "digit82/ko-bart-summary"

class SummaryService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("⏳ 요약 모델 로딩 중...")
            cls._instance = super().__new__(cls)
            cls.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
            cls.model = BartForConditionalGeneration.from_pretrained(model_name)
        return cls._instance

    def generate_summary(self, text: str) -> str:
        if not text or len(text) < 10:
            return "내용이 너무 짧아 요약할 수 없습니다."

        raw_input_ids = self.tokenizer.encode(text)
        input_ids = [self.tokenizer.bos_token_id] + raw_input_ids + [self.tokenizer.eos_token_id]

        # 요약 생성 시 M4 CPU 최적화 파라미터 적용
        summary_ids = self.model.generate(
            torch.tensor([input_ids]),
            max_length=128,
            num_beams=4,
            eos_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

summary_service = SummaryService() # 싱글톤 인스턴스
